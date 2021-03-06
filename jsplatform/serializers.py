import sys

from django.apps import apps
from django.forms.models import model_to_dict
from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer

from .models import (
    Answer,
    Category,
    Exam,
    Exercise,
    FrontendError,
    GivenAnswer,
    Question,
    Submission,
    TestCase,
)


class FrontendErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontendError
        fields = "__all__"


# todo make ExamPreviewSerializer
class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "draft",
            "begin_timestamp",
            "end_timestamp",
        ]

    def __init__(self, *args, **kwargs):
        super(ExamSerializer, self).__init__(*args, **kwargs)
        if self.context["request"].user.is_teacher:
            # if requesting user is a teacher, show all exercises and questions for this exam
            self.fields["exercises"] = ExerciseSerializer(many=True, **kwargs)
            self.fields["questions"] = QuestionSerializer(many=True, **kwargs)
            self.fields["categories"] = CategorySerializer(many=True, **kwargs)
            self.fields["randomize_questions"] = serializers.BooleanField()
            self.fields["randomize_exercises"] = serializers.BooleanField()
            self.fields["created_by"] = UserSerializer(read_only=True)
            self.fields["allowed_teachers"] = serializers.PrimaryKeyRelatedField(
                many=True,
                required=False,
                queryset=User.objects.filter(is_teacher=True),
            )
            self.fields["closed"] = serializers.BooleanField(required=False)
            self.fields["locked_by"] = serializers.SerializerMethodField(read_only=True)
            self.fields["closed_at"] = serializers.DateTimeField(read_only=True)
        else:
            # if requesting user isn't a teacher, show only the exercise/question that's
            # currently assigned to them
            self.fields["exercise"] = serializers.SerializerMethodField()
            self.fields["submissions"] = serializers.SerializerMethodField()
            self.fields["question"] = serializers.SerializerMethodField()

    def create(self, validated_data):
        questions = validated_data.pop("questions")
        exercises = validated_data.pop("exercises")
        categories = validated_data.pop("categories")
        allowed_teachers = validated_data.pop("allowed_teachers")

        exam = Exam.objects.create(**validated_data)
        exam.allowed_teachers.set(allowed_teachers)

        # create categories
        for category in categories:
            c = CategorySerializer(data=category, context=self.context)
            c.is_valid(raise_exception=True)
            c.save(exam=exam)

        # create objects for each question and exercise
        for question in questions:
            # get the category this question referenced in the creation form
            cat = Category.objects.get(tmp_uuid=question.pop("category_uuid"))

            q = QuestionSerializer(data=question, context=self.context)
            q.is_valid(raise_exception=True)
            q.save(exam=exam, category=cat)
        for exercise in exercises:
            # get the category this exercise referenced in the creation form
            cat = Category.objects.get(tmp_uuid=exercise.pop("category_uuid"))

            e = ExerciseSerializer(data=exercise, context=self.context)
            e.is_valid(raise_exception=True)
            e.save(exam=exam, category=cat)

        return exam

    def update(self, instance, validated_data):
        # get data about exercises and questions
        questions_data = validated_data.pop("questions")
        exercises_data = validated_data.pop("exercises")
        categories_data = validated_data.pop("categories")

        # update Exam instance
        instance = super(ExamSerializer, self).update(instance, validated_data)

        questions = instance.questions.all()
        exercises = instance.exercises.all()
        categories = instance.categories.all()

        # update each category
        for category_data in categories_data:
            if category_data.get("id") is not None:
                category = Category.objects.get(pk=category_data["id"])
                save_id = category_data.pop("id")
            else:
                category = Category(exam=instance)
                category.save()
                save_id = category.pk

            serializer = CategorySerializer(
                category, data=category_data, context=self.context
            )
            serializer.is_valid(raise_exception=True)

            # update category
            serializer.update(instance=category, validated_data=category_data)

            # remove category from the list of those still to process
            categories = categories.exclude(pk=save_id)

        # # remove any categories for which data wasn't sent (i.e. user deleted them)
        for category in categories:
            category.delete()

        # update each question
        for question_data in questions_data:
            if question_data.get("id") is not None:  # try:
                question = Question.objects.get(pk=question_data["id"])
                save_id = question_data.pop("id")  # question_data["id"]
            else:  # except Question.DoesNotExist:
                question = Question(exam=instance)
                question.save()
                save_id = question.pk

            serializer = QuestionSerializer(
                question, data=question_data, context=self.context
            )

            # pop question category as it's not handled by the serializer
            question_category = question_data.pop("category", None)

            # question belongs to a new category we just created
            if question_category is None:
                question_category = Category.objects.get(
                    tmp_uuid=question_data["category_uuid"]
                )

            serializer.is_valid(raise_exception=True)

            # update question
            updated_question = serializer.update(
                instance=question, validated_data=question_data
            )
            # update question category
            updated_question.category = question_category
            updated_question.save()

            # remove question from the list of those still to process
            questions = questions.exclude(pk=save_id)

        # remove any questions for which data wasn't sent (i.e. user deleted them)
        for question in questions:
            question.delete()

        # update each exercise
        for exercise_data in exercises_data:
            if exercise_data.get("id") is not None:  # try:
                exercise = Exercise.objects.get(pk=exercise_data["id"])
                save_id = exercise_data.pop("id")  # exercise_data["id"]
            else:  # except Exercise.DoesNotExist:
                exercise = Exercise(exam=instance)
                exercise.save()
                save_id = exercise.pk

            serializer = ExerciseSerializer(
                exercise, data=exercise_data, context=self.context
            )

            # pop exercise category as it's not handled by the serializer
            exercise_category = exercise_data.pop("category", None)

            # exercise belongs to a new category we just created
            if exercise_category is None:
                exercise_category = Category.objects.get(
                    tmp_uuid=exercise_data["category_uuid"]
                )

            serializer.is_valid(raise_exception=True)

            # update exercise
            updated_exercise = serializer.update(
                instance=exercise, validated_data=exercise_data
            )
            # update exercise category
            updated_exercise.category = exercise_category
            updated_exercise.save()

            # remove exercise from the list of those still to process
            exercises = exercises.exclude(pk=save_id)

        # remove any exercises for which data wasn't sent (i.e. user deleted them)
        for exercise in exercises:
            exercise.delete()

        return instance

    def get_exercise(self, obj):
        try:
            return ExerciseSerializer(
                instance=self.context["exercise"],
                context={"request": self.context["request"]},
            ).data
            # todo use proper exception
        except Exception:
            return None

    def get_question(self, obj):
        try:
            return QuestionSerializer(
                instance=self.context["question"],
                context={"request": self.context["request"]},
            ).data
            # todo use proper exception
        except Exception:
            return None

    def get_submissions(self, obj):
        try:
            return SubmissionSerializer(
                instance=self.context["submissions"],
                context={"request": self.context["request"]},
                many=True,
            ).data
            # todo use proper exception
        except Exception:
            return None

    def get_locked_by(self, obj):
        # todo see if you can just use a ReadOnlyField
        return obj.locked_by.full_name if obj.locked_by is not None else None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "tmp_uuid",
            "item_type",
            "amount",
            "is_aggregated_question",
            "introduction_text",
            "randomize",
        ]

    def __init__(self, *args, **kwargs):
        super(CategorySerializer, self).__init__(*args, **kwargs)
        self.fields["id"] = serializers.IntegerField(required=False)
        self.fields["tmp_uuid"] = serializers.UUIDField(
            format="hex_verbose", write_only=True, required=False
        )

        if not self.context["request"].user.is_teacher:
            self.fields["introduction_text"] = serializers.CharField(
                source="rendered_introduction_text"
            )


class TestCaseSerializer(serializers.ModelSerializer):
    """
    A serializer for TestCase model showing its associated assertion and public/secret status
    """

    class Meta:
        model = TestCase
        fields = ["id", "assertion", "is_public"]

    def __init__(self, *args, **kwargs):
        super(TestCaseSerializer, self).__init__(*args, **kwargs)
        self.fields["id"] = serializers.IntegerField(required=False)

    def create(self, validated_data):
        instance = TestCase.objects.create(**validated_data)
        return instance


class QuestionSerializer(serializers.ModelSerializer):
    """
    A serializer for a multiple choice question, showing its text and answers
    """

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "accepts_multiple_answers",
            "num_appearances",
        ]

    def __init__(self, *args, **kwargs):
        super(QuestionSerializer, self).__init__(*args, **kwargs)
        self.fields["answers"] = AnswerSerializer(many=True, **kwargs)
        # self.fields["text"] = serializers.SerializerMethodField()
        # todo limit categories to those of the same exam as the question's
        self.fields["category"] = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all(), required=False
        )
        self.fields["category_name"] = serializers.ReadOnlyField(source="category.name")
        # ! keep an eye on this
        self.fields["id"] = serializers.IntegerField(required=False)
        self.fields["introduction"] = serializers.ReadOnlyField(
            source="category.introduction_text"
        )
        # used to temporarily reference a newly created category from the frontend
        self.fields["category_uuid"] = serializers.UUIDField(
            write_only=True, required=False
        )

        if not self.context["request"].user.is_teacher:
            # show text with TeX rendered as svg instead of the source
            # text to non-teacher users
            self.fields["text"] = serializers.CharField(source="rendered_text")

    def get_text(self, obj):
        return (
            obj.text if self.context["request"].user.is_teacher else obj.rendered_text
        )

    def create(self, validated_data):
        answers = validated_data.pop("answers")

        question = Question.objects.create(**validated_data)

        # create objects for each answer
        for answer in answers:
            Answer.objects.create(question=question, **answer)

        return question

    def update(self, instance, validated_data):
        # get data about answers
        answers_data = validated_data.pop("answers")
        # update question instance
        instance = super(QuestionSerializer, self).update(instance, validated_data)

        answers = instance.answers.all()

        # update each answer
        for answer_data in answers_data:
            if answer_data.get("id") is not None:  # try:
                answer = Answer.objects.get(pk=answer_data["id"])
                save_id = answer_data.pop("id")  # answer_data["id"]
            else:  # except Answer.DoesNotExist:
                answer = Answer(question=instance)
                answer.save()
                save_id = answer.pk

            serializer = AnswerSerializer(
                answer, data=answer_data, context=self.context
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=answer, validated_data=answer_data)

            # remove answer from the list of those still to process
            answers = answers.exclude(pk=save_id)

        # remove any answers for which data wasn't sent (i.e. user deleted them)
        for answer in answers:
            answer.delete()

        return instance


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text"]

    def __init__(self, *args, **kwargs):
        super(AnswerSerializer, self).__init__(*args, **kwargs)
        self.fields["id"] = serializers.IntegerField(required=False)
        if self.context["request"].user.is_teacher:
            # only show whether this is the right answer and how many times it
            # was selected to teachers
            self.fields["is_right_answer"] = serializers.BooleanField()
            self.fields["selections"] = serializers.IntegerField(read_only=True)
        else:
            # show text with TeX rendered as svg instead of the source
            # text to non-teacher users
            self.fields["text"] = serializers.CharField(source="rendered_text")


class ExerciseSerializer(serializers.ModelSerializer):
    """
    A serializer for Exercise model, which can conditionally show either all test cases
    or public test cases only for the exercise
    """

    class Meta:
        model = Exercise
        fields = [
            "id",
            "text",
            "starting_code",
            "min_passing_testcases",
            "num_appearances",
        ]

    def __init__(self, *args, **kwargs):
        super(ExerciseSerializer, self).__init__(*args, **kwargs)

        # used to temporarily reference a newly created category on the frontend
        self.fields["category_uuid"] = serializers.UUIDField(
            write_only=True, required=False
        )

        self.fields["category"] = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all(), required=False
        )

        if self.context["request"].user.is_teacher:
            self.fields["testcases"] = TestCaseSerializer(many=True)
            # !
            self.fields["id"] = serializers.IntegerField(required=False)
        else:
            # only show public test cases to non-staff users
            self.fields["public_testcases"] = TestCaseSerializer(
                many=True, read_only=True
            )
            self.fields["text"] = serializers.CharField(source="rendered_text")

    def create(self, validated_data):
        testcases = validated_data.pop("testcases")

        exercise = Exercise.objects.create(**validated_data)

        # create TestCase objects for each test case
        for testcase in testcases:
            TestCase.objects.create(exercise=exercise, **testcase)

        return exercise

    def update(self, instance, validated_data):
        # get data about test cases
        testcases_data = validated_data.pop("testcases")

        # update Exercise instance
        instance = super(ExerciseSerializer, self).update(instance, validated_data)

        testcases = instance.testcases.all()

        # update each test case
        for testcase_data in testcases_data:
            if testcase_data.get("id") is not None:  # try:
                testcase = TestCase.objects.get(pk=testcase_data["id"])
                save_id = testcase_data.pop("id")  # testcase_data["id"]
            else:  # except TestCase.DoesNotExist:
                testcase = TestCase(exercise=instance)
                testcase.save()
                save_id = testcase.pk

            serializer = TestCaseSerializer(
                testcase, data=testcase_data, context=self.context
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=testcase, validated_data=testcase_data)

            # remove testcase from the list of those still to process
            testcases = testcases.exclude(pk=save_id)

        # remove any testcases for which data wasn't sent (i.e. user deleted them)
        for testcase in testcases:
            testcase.delete()

        return instance


class GivenAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivenAnswer
        fields = ["id", "user", "answer", "text", "timestamp"]
        read_only_fields = ["user", "timestamp"]


class SubmissionSerializer(serializers.ModelSerializer):
    """
    A serializer for Submission model showing the submitted code, the timestamp, and the
    details of the submission regarding the test cases
    """

    class Meta:
        model = Submission
        fields = [
            "id",
            "user",
            "code",
            "timestamp",
            "is_eligible",
            "has_been_turned_in",
        ]
        read_only_fields = ["is_eligible", "user", "has_been_turned_in"]

    def __init__(self, *args, **kwargs):
        super(SubmissionSerializer, self).__init__(*args, **kwargs)

        if self.context["request"].user.is_teacher:
            self.fields["details"] = serializers.JSONField(read_only=True)
        else:
            # only show public test case details to non-staff users
            self.fields["public_details"] = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        submission = Submission.objects.create(**validated_data)

        return submission
