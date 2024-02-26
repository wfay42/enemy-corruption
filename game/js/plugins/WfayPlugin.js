
/*:
 * @target MZ
 * @plugindesc Wfay42's test plugin
 * @author wfay42 https://www.deviantart.com/wfay42
 *
 * @help WfayPlugin.js
 *
 * This plugin is testing stuff out
 *
 * @command set
 * @text Set a string value
 * @desc sets a value for testing
 *
 * @arg text
 * @type multiline_string
 * @text Text
 * @desc Text to test with
 *
 * @command WhoInTroop
 * @text Who In Troop
 * @desc Display text for who is in the enemy Troop
 *
 */
(() => {
    const pluginName = "WfayPlugin";
    let foo = "";

    PluginManager.registerCommand(pluginName, "set", args => {
        foo = String(args.text)
    });

    PluginManager.registerCommand(pluginName, "WhoInTroop", args => {
        // TODO: you should only trigger this during a battle. I'm having trouble getting this to show up,
        // but that could be because I'm invoking it at the wrong time
        console.log("In WhoInTroop");
        $gameMessage.add("My message");
        for (const name of $gameTroop.enemyNames()) {
            $gameMessage.add(TextManager.emerge.format(name));
        }
        console.log("In WhoInTroop");
    });

    /**
     * What I want this plugin to do:
     *
     * 1. Maintain a mapping of an enemy, and its different phases as it transforms
     * 2. Logic to move an enemy through that mapping
     * 3. Be able to apply that logic against all enemies within a battle
     * 4a. Be able to run this Plugin Command at the end of each turn
     * 4b. (Bonus points) actually be able to run this Plugin Command after any actor's move
     */
})();
