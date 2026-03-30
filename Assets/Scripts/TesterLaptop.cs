using UnityEngine;
using System.Collections.Generic;
using UnityEngine.InputSystem;

public class TesterLaptop : MonoBehaviour
{
    public List<GameObject> all_lamps;
    public List<GameObject> some_drawers;
    public InteractionManager interactionManager;

    void Update()
    {
        var keyboard = Keyboard.current;

        if (keyboard == null) return;

        // lamps, keys 1 to 5
        if (keyboard.digit1Key.wasPressedThisFrame) TriggerLamp(0);
        if (keyboard.digit2Key.wasPressedThisFrame) TriggerLamp(1);
        if (keyboard.digit3Key.wasPressedThisFrame) TriggerLamp(2);
        if (keyboard.digit4Key.wasPressedThisFrame) TriggerLamp(3);
        if (keyboard.digit5Key.wasPressedThisFrame) TriggerLamp(4);

        // TV, key 6
        if (keyboard.digit6Key.wasPressedThisFrame)
        {
            Debug.Log("pressed 6");
            if (interactionManager != null)
                interactionManager.SetTV();
        }

        if (keyboard.digit7Key.wasPressedThisFrame) TriggerDrawer(0);
        if (keyboard.digit8Key.wasPressedThisFrame) TriggerDrawer(1);
    }

    private void TriggerLamp(int index)
    {
        if (interactionManager == null) return;
        if (all_lamps == null || index < 0 || index >= all_lamps.Count) return;

        GameObject lamp = all_lamps[index];

        if (lamp != null)
            interactionManager.SetLight(lamp);
    }

    private void TriggerDrawer(int index)
    {
        if (interactionManager == null) return;
        if (some_drawers == null || index < 0 || index >= some_drawers.Count) return;

        GameObject drawer = some_drawers[index];

        if (drawer != null)
            interactionManager.SetDrawer(drawer);
    }
}