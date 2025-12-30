response = agent.invoke(
        {"messages": [{"role": "user", "content": maintenance_query}]},
        config=config,
        context=Context(user_id="1")
    )

print(response["messages"])