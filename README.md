# EMAIL2TEXT

Simple chat bot integration for free text bots.

## Recieving income messages:
```
def handle_messages(message, From):
    if message == "hello""
        bot.send_message("hi", From) #reply to the user
    else:
        bot.send_message("bye", From)
bot = TextBot(username, password, imap, smtp, handle_messages=handle_messages)
bot.start()
```
## Using commands
```
def hello(message, From):
    bot.send_message("hi", From)
def bye(message, From):
    bot.send_message("bye", From)
bot = TextBot(username, password, imap, smtp)
bot.addCommand("hello", hello)
bot.addCommand("bye", bye)
bot.start()
```