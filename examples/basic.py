from shieldx import Shield
from shieldx.validators.text import MaxLengthValidator, BlockedWordsValidator
from shieldx.validators.json import ValidJSONValidator

shield = Shield(name="demo")
shield.use(MaxLengthValidator(100))
shield.use(BlockedWordsValidator(["stupid", "idiot"]))

text_report = shield.validate("you are stupid")
print(text_report.summary())

json_shield = Shield(name="json-demo")
json_shield.use(ValidJSONValidator())

json_report = json_shield.validate('{"name": "Ali"}')
print(json_report.summary())