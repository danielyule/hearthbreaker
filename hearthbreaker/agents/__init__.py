from hearthbreaker.agents.agent_registry import AgentRegistry as __ar__
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent

registry = __ar__()

registry.register("Random", RandomAgent)
registry.register("Trade", TradeAgent)