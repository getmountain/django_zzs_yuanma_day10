v1 = "non_field_errors.xxxx"

data_list = v1.split(".")

form = "xx"
for name in data_list:
    # form.non_field_errors
    data = getattr(form, name)
    if callable(data):
        form = data()  # form.non_field_errors().xxxx()
    else:
        form = data  # form.non_field_errors.xxxx
