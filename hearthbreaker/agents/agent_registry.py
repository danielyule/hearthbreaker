class AgentRegistry:
    def __init__(self):
        super().__init__()
        self.__registry = {}

    def register(self, name, agent_class):
        self.__registry[name] = agent_class

    def create_agent(self, name):
        if name in self.__registry:
            return self.__registry[name]()
        else:
            raise KeyError("{} is not in the agent registry".format(name))

    def get_names(self):
        return [name for name in self.__registry.keys()]
