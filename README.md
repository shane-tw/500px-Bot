This bot was developed with the purpose of automating tedious tasks on [500px](https://500px.com/), a website for designers to share samples of their work with each other.
The general idea is to basically earn yourself 500px followers while not following thousands who have no intentional in following you back.
# What It Does
* It obtains a list of newly registered users on 500px's [Upcoming](https://500px.com/upcoming) page.
* It follows `numFollowsWanted` users on that list, ignoring users already followed, every day.
* Every two days, if the user followed hasn't followed the bot back, the user is unfollowed and blacklisted by the bot.
* Once a user has been on a list, be it the list of followed users, or the blacklisted users, for a week, their name is purged from the applicable list(s) and there is a chance that the bot may attempt to follow them again in the future, due to users being capable of entering the Upcoming page an infinite number of times.
