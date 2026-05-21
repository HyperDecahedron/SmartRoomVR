using UnityEngine;

public class InteractableObject : MonoBehaviour
{
    public bool isDrawer = false;

    private Outline outline;
    private InteractionManager interactionManager;

    private void Start()
    {
        if (isDrawer)
            outline = transform.parent.parent.GetComponent<Outline>();
        else
            outline = GetComponent<Outline>();

        if (outline != null)
        {
            outline.enabled = false; // starts disabled
        }

        interactionManager = GameObject.FindWithTag("InteractionManager").GetComponent<InteractionManager>();
    }

    private void OnTriggerEnter(Collider collision)
    {
        if (collision.gameObject.CompareTag("Pointer"))
        {
            if (outline != null)
            {
                outline.enabled = true;
            }

            interactionManager.current_object = this.gameObject;
        }
    }

    private void OnTriggerExit(Collider collision)
    {
        if (collision.gameObject.CompareTag("Pointer"))
        {
            if (outline != null)
            {
                outline.enabled = false;
            }

            interactionManager.current_object = null;
        }
    }
}