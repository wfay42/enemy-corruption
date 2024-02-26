
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
    const clownyState = 32;
    let foo = "";

    PluginManager.registerCommand(pluginName, "set", args => {
        foo = String(args.text)
    });

    // map "before" enemyId to "after" enemyId
    const clownyLookupTable = new Map();
    clownyLookupTable.set(1, 2);
    clownyLookupTable.set(2, 3);

    // map states (such as clowny) to a table mapping transformations
    const stateLookupTable = new Map();
    stateLookupTable.set(clownyState, clownyLookupTable);

    const lookupFunction = function(stateId, enemyId) {
        const lookupTable = stateLookupTable.get(stateId);
        if (lookupTable) {
            return lookupTable.get(enemyId);
        }
        return null;
    };

    PluginManager.registerCommand(pluginName, "WhoInTroop", args => {
        for (const game_enemy of $gameTroop.members()) {
            $gameMessage.add("Enemy: " + game_enemy.name());
            if (game_enemy.isStateAffected(clownyState)) {

                const newEnemyId = lookupFunction(clownyState, game_enemy.enemyId());
                if (newEnemyId) {
                    game_enemy.transform(newEnemyId);
                }
                game_enemy.eraseState(clownyState);
            }

        }
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
