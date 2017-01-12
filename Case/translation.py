# translation.py: This file is used by djando-modeltranlate library to define
# every field to be translate in each model defined in Case app.
# According to each language defined in vsf/settings.py,
# the library will create a column in DB to every field.

from modeltranslation.translator import translator, TranslationOptions
from .models import Case, Category, Update


# CategoryTranslationOptions: this class define the fields in Category model
# to be translate. By default, the new columns in db will be nullable.
class CategoryTranslationOptions(TranslationOptions):
    fields = ('display_name',)


# CaseTranslationOptions: this class define the fields in Case model
# to be translate. By default, the new columns in db will be nullable.
class CaseTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


# UpdateTranslationOptions: this class define the fields in Update model
# to be translate. By default, the new columns in db will be nullable.
class UpdateTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


# This actions allow the library to create relationship between Case app models
# and TranslationOptions defined in this file
translator.register(Category, CategoryTranslationOptions)
translator.register(Case, CaseTranslationOptions)
translator.register(Update, UpdateTranslationOptions)
