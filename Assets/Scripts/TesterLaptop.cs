using UnityEngine;
using UnityEngine.InputSystem;

public class TesterLaptop : MonoBehaviour
{
    private InteractionManager interactionManager;

    private void Start()
    {
        interactionManager = GameObject.FindWithTag("InteractionManager").GetComponent<InteractionManager>();
    }

    private void Update()
    {
        if (Keyboard.current.spaceKey.wasPressedThisFrame)
        {
            if (interactionManager != null)
            {
                interactionManager.SelectObject();
            }
        }
    }
}