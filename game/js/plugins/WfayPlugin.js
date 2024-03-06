
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

    // map states (such as clowny) to a table mapping transformations
    const stateLookupTable = new Map();
    stateLookupTable.set(clownyState, clownyLookupTable);
    stateLookupTable.set(femmeFataleState, femmeFataleLookupTable);

    /**
     *
     * @param {*} stateId ID of state to add to the table (like Poison)
     * @param {*} enemyIdArr array of enemyIDs to transition through, in order.
     * E.g. [1,2,3] means 1 can transition to 2, and 2 can transition to 3
     */
    const addToLookupTable = function(stateId, enemyIdArr) {
        let lookupTable = stateLookupTable.get(stateId);
        if (!lookupTable) {
            lookupTable = new Map();
            stateLookupTable.set(stateId, lookupTable);
        }
        let i = 0;
        let j = 0;
        while (i < enemyIdArr.length - 1) {
            enemyId1 = enemyIdArr[i];
            enemyId2 = enemyIdArr[i + 1];
            lookupTable.set(enemyId1, enemyId2);
            i++;
        }
    }

    addToLookupTable(maidState, [4, 7, 8]);

    /**
     *
     * @param {*} stateId ID of state to lookup (like Poison)
     * @param {*} enemyId ID of enemy to lookup
     * @returns integer enemyID, or null if not found
     */
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
