from polls.views import persons, events, rooms

def main():
    for event in events:
        print(event.date)

main()
