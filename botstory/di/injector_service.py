import inspect


class Scope:
    def __init__(self):
        self.storage = {}

    def get(self, type_name):
        item = self.storage[type_name]
        if inspect.isclass(item):
            return item()
        else:
            return item

    def register(self, type_name, value):
        self.storage[type_name] = value


class Injector:
    def __init__(self):
        self.root = Scope()
        # all instances that are singletones
        self.singleton_cache = {}
        # functions that waits for deps
        self.requires_fns = {}
        # instances that will autoupdate on each new instance come
        self.auto_update_list = []

    def register(self, type_name, instance):
        self.root.register(type_name, instance)
        for wait_instance in self.auto_update_list:
            self.bind(wait_instance)

    def requires(self, fn):
        fn_sig = inspect.signature(fn)
        self.requires_fns[fn] = {
            key: {'default': fn_sig.parameters[key].default}
            for key in fn_sig.parameters.keys() if key != 'self'}

    def bind(self, instance, autoupdate=False):
        methods = [
            (m, cls.__dict__[m])
            for cls in inspect.getmro(type(instance))
            for m in cls.__dict__ if inspect.isfunction(cls.__dict__[m])
            ]

        requires_of_methods = [(method_ptr, {dep: self.get(dep) or dep_spec['default']
                                             for dep, dep_spec in
                                             self.requires_fns.get(method_ptr, {}).items()})
                               for (method_name, method_ptr) in methods]

        for (method_ptr, method_deps) in requires_of_methods:
            if len(method_deps) > 0:
                method_ptr(instance, **method_deps)

        if autoupdate:
            self.auto_update_list.append(instance)

        return instance

    def clear(self):
        self.root = Scope()
        self.singleton_cache = {}
        self.requires_fns = {}

    def get(self, type_name):
        try:
            return self.singleton_cache[type_name]
        except KeyError:
            try:
                instance = self.root.get(type_name)
            except KeyError:
                # TODO: sometimes we should fail loudly in this case
                return None

            self.singleton_cache[type_name] = instance
            instance = self.bind(instance)

        return instance