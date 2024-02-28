
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
    const femmeFataleState = 33;
    const maidState = 34;
    let foo = "";

    PluginManager.registerCommand(pluginName, "set", args => {
        foo = String(args.text)
    });

    // map "before" enemyId to "after" enemyId
    const clownyLookupTable = new Map();
    clownyLookupTable.set(1, 2);
    clownyLookupTable.set(2, 3);

    const femmeFataleLookupTable = new Map();
    femmeFataleLookupTable.set(4, 5);
    femmeFataleLookupTable.set(5, 6);

    const maidLookupTable = new Map();
    maidLookupTable.set(4, 7);
    maidLookupTable.set(7, 8);

    // map states (such as clowny) to a table mapping transformations
    const stateLookupTable = new Map();
    stateLookupTable.set(clownyState, clownyLookupTable);
    stateLookupTable.set(femmeFataleState, femmeFataleLookupTable);
    stateLookupTable.set(maidState, maidLookupTable);

    const lookupFunction = function(stateId, enemyId) {
        const lookupTable = stateLookupTable.get(stateId);
        if (lookupTable) {
            return lookupTable.get(enemyId);
        }
        return null;
    };

    PluginManager.registerCommand(pluginName, "WhoInTroop", args => {
        for (const game_enemy of $gameTroop.members()) {
            for (const state_name of [clownyState, femmeFataleState, maidState]) {
                if (game_enemy.isStateAffected(state_name)) {

                    const newEnemyId = lookupFunction(state_name, game_enemy.enemyId());
                    if (newEnemyId) {
                        game_enemy.transform(newEnemyId);
                    }
                    game_enemy.eraseState(state_name);
                    break;
                }
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
