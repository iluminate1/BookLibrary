from django import forms
from django.contrib.auth import get_user_model
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ""
        error_list = [
            f'<div class="error__item" style="margin-bottom: 5px;">{e}</div>'
            for e in self
        ]
        error_list_string = "".join(error_list)
        error_item_style = "font-family: monospace; font-style: italic; color: #c44a4a; text-align: center; margin-bottom: 5px;"
        return mark_safe(
            f'<div class="form__error-list" style="{error_item_style}">{error_list_string}</div>'
        )
