# Miniscape

## Tutorial
If you are new to the game, welcome! Below is a list of the most important commands you need to know to start out:

* `~starter` gives you a starter kit of items.
* `~items [search]` shows your inventory. Adding an argument searches for items with a particular word.
* `~items info [item]` shows more information about a particular item.
* `~equip` equips an item.
* `~me` shows your current stats and equipment.

In addition, here are some of the main activities you can partake in:

* `~kill [number] [monster] [length: minutes]` kills either a given number of monsters, or kills or a monster for a set period of time for combat experience.
* `~bestiary [monster]` shows the list of monsters you can kill. Specifying a monster will show more info related to that monster.
* `~slayer` starts a slayer task for slayer experience.
* `~gather [number] [item] [length: minutes]` gathers either a given number of items, or gathers an item for a set period of time for gathering experience.
* `~quest` shows the list of quests you can currently start.
* `~shop` shows the items you can buy.
* `~buy [number] [item]` buys a given number of an item.
* `~sell [number] [item]` sells a given number of an item, or all if `[number]` is `all`.
* `~trade [user] [number] [item] [offer]` sells a given number of an item to a user for a given offer.
* `~cancel` cancels whatever action you are currently doing.

You do not have to do all of these. You can focus on just killing goblins with your fists for all I care. Some more activities you can enjoy are listed in the **commands** section of this page.

If you have any questions, feel free to ask around on the MiniScape disord channel, which can be found here: https://discord.gg/vj59hYB.

## Commands
These commands are organised by category.

Adventure commands:
* `~bury` buries items for prayer xp.
* `~cancel` cancels whatever action you are currently doing.
* `~clue [difficulty]` does a clue scroll of a given difficulty, provided you have it in your inventory.
* `~gather [number] [item] [length: minutes]` sets up a gathering session of a particular item for a given length of time or until you have gathered a given number of that item
* `~kill [number] [monster] [length: minutes]` allows you to fight a particular monster for a given length of time or until you've killed a given number of that monster.
* `~quests` shows a list of quests that you can do.
* `~quests [quest number]` shows information related to a specific quest.
* `~quests start [quest number]` starts a particular quest.
* `~rc [number] [rune]` starts a runecrafting session.
* `~slayer` gives a slayer task.
* `~starter` gives new players a set of bronze armour to start off.
* `~status` shows you what you are currently doing, if you are in the middle of doing something.

Bank Commands: 
* `~balance [user]` shows a user's balance. It shows your own if you do not give an argument.
* `~bestiary [monster]` shows a list of all monsters in the game. Specifying a specific monster shows more data specific to that monster.
* `~claim [item]` can be used to receive items from keys, gem stones, and other objects.
* `~compare "[item1]" "[item2]"` compares the stats of two items.
* `~cook [number] [cooked item]` cooks (a given number) of items.
* `~craft [number] [item]` crafts (a given number of) items.
* `~eat [food]` sets the food you want eaten while you go on tasks.
* `~equip [item]` allows you to equip an item from your inventory.
* `~items` shows your inventory.
* `~items [search]` allows you to search for items that contain the string `[search]` in your inventory.
* `~items info [item]` allows you to see the stats and drop sources of a particular item.
* `~items lock [item]` locks an item in your inventory to prevent it from being accidentally sold.
* `~items unlock [item]` unlocks an item in your inventory to allow it to be sold again.
* `~leaderboard [name]` shows the leaderboard of total levels 
* `~me` shows your current levels, equipment, and other stats.
* `~pray` shows the prayers you can use.
* `~pray [prayer]` sets your prayer.
* `~pray info [prayer]` shows information about a prayer.
* `~recipes` shows you a list of items you can craft
* `~recipes info [item]` shows you the information of one craftable item.
* `~tolevel [level] [skill]` shows how much xp you need to get to a certain level in a skill.
* `~unequip [item]` allows you to unequip an item from your equipment.

Store Commands:
* `~buy [item]` buys an item from the shop
* `~shop` shows the items that are currently on stock
* `~sell [number] [item]` sells (a given number of) an item to the store
* `~sellall [max value]` sells all items (up to but not including a given max value) from a user's inventory to the store.
* `~trade [name] [number] [item] [offer]` trades with another player.

Other Commands:
* `~dm [user] [amount]` allows you to fight another user.
* `~ship [user] [user2]` allows you to ship two users.
* `~shipall [user]` allows you to ship someone between everyone in the server and shows the top ten.
* `~shipall [user] b` shows the bottom ten ranked ships between someone and the rest of the server.
* `~snap [user]` tells whether a user has survived Thanos's snap.

Admin Commands (needs manage channels permission):
* `~addblacklist [channel(s)] ...` adds channels to the server's blacklist.
* `~addwhitelist [channel(s)] ...` adds channels to the server's whitelist.
* `~listchannels` shows which channels are in your server's white/blacklist.
* `~removeac [channel]` removes the announcement channel.
* `~removeblacklist [channel(s)] ...` remove channels from the server's blacklist.
* `~removewhitelist [channel(s)] ...` remove channels from the server's whitelist.
* `~setac [channel]` sets the announcement channel. The default behaviour is to send the announcement to the channel from which the user sent the command.
