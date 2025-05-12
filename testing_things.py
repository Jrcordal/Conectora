import phonenumbers

text ='+31610260496'
text2 = '0031610260496'
text3='0610260496'

phone1 = phonenumbers.parse(text)
phone2 = phonenumbers.parse(text2, "NL")
phone3 = phonenumbers.parse(text3, "NL")

print(phonenumbers.is_valid_number(phone1))
print(phonenumbers.is_valid_number(phone2))
print(phonenumbers.is_valid_number(phone3))


print(phone1)
print(phone2)
print(phone3)



