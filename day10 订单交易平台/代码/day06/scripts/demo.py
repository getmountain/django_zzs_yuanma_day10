class ErrorDict(dict):

    def __str__(self):
        self.as_ul()
        return "哈哈哈"

    def as_p(self):
        for k, v in self.items():
            tpl = "<p>{}</p>".format(k)
            print(tpl)

    def as_ul(self):
        for k, v in self.items():
            tpl = "<li>{}</li>".format(k)
            print(tpl)


obj = ErrorDict()
obj['k1'] = [123, 456]
obj['k2'] = [666, 999]
# print(obj)
# obj.as_ul()
# print(obj)

print(obj['k1'][0])
