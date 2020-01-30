from django import forms
from .models import emCheckRecord, emFatpDetail

from datetime import datetime


class CustomModelChoiceIterator(forms.models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj),
                self.field.label_from_instance(obj), obj)


class CustomModelChoiceField(forms.models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CustomModelChoiceIterator(self)
    choices = property(_get_choices,
                       forms.fields.MultipleChoiceField._set_choices)


class emCheckRecordForm(forms.ModelForm):
    class Meta:
        model = emCheckRecord
        fields = ['formCheckItems', 'checkOwner', 'checkFile']

    # formCheckItems = forms.ModelMultipleChoiceField(
    formCheckItems = CustomModelChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=None
    )

    def __init__(self, *args, **kwargs):
        self._station = kwargs.pop('station', None)
        self._line = kwargs.pop('line', None)
        super(emCheckRecordForm, self).__init__(*args, **kwargs)

        self.fields['formCheckItems'].queryset = self._station.checkItems.all()

        #widget add css class
        self.fields['checkOwner'].widget.attrs['placeholder'] = 'input owner'
        self.fields['checkOwner'].widget.attrs['class'] = 'form-control'
        self.fields['checkFile'].widget.attrs['class'] = 'custom-file-input'