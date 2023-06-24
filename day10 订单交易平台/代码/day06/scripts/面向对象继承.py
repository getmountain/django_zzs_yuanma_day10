class BootStrapForm(object):
    exclude_data_list = []

    def __init__(self):
        print(self.exclude_data_list)


class UserForm(BootStrapForm):
    exclude_data_list = [11, 22, 33]


v1 = BootStrapForm()  # []
v2 = UserForm()  # [11, 22, 33]
v3 = UserForm()  #
