from django import forms
from django.forms import inlineformset_factory

from main.models import Bb, AdditionalImage


class SubRubricForm(forms.ModelForm):
    pass
    # super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), empty_label=None,
    #                                       label="Надрубрика", required=True)

    # class Meta:
    #     model = SubRubric
    #     fields = "__all__"


class BbForm(forms.ModelForm):
    class Meta:
        model = Bb
        fields = "__all__"
        widgets = {"author": forms.HiddenInput}


AiFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')
