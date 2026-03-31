using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class HeadRaycast : MonoBehaviour
{
    public InteractionManager interactionManager;

    private float maxDistance = 8f;
    private float yOffset = -0.1f;
    private LineRenderer lineRenderer;
    private GameObject prevObject = null;

    private readonly Color validHitColor = new Color32(0x00, 0xFF, 0xE3, 0xFF);
    private readonly Color defaultColor = new Color32(0xFF, 0xFF, 0xFF, 150);

    private void Awake()
    {
        lineRenderer = GetComponent<LineRenderer>();
        if (lineRenderer != null)
        {
            lineRenderer.positionCount = 2;
        }
    }

    private void Update()
    {
        PerformRaycast();
    }

    private void PerformRaycast()
    {
        Vector3 rayStart = transform.position + Vector3.up * yOffset; // upward offset
        Vector3 rayDirection = transform.forward;

        Vector3 endPoint = rayStart + rayDirection * maxDistance;
        Color currentColor = defaultColor;

        if (Physics.Raycast(rayStart, rayDirection, out RaycastHit hit, maxDistance))
        {
            endPoint = hit.point;

            if (hit.collider.CompareTag("Light") ||
                hit.collider.CompareTag("Drawer") ||
                hit.collider.CompareTag("TV"))
            {
                currentColor = validHitColor;

                if (hit.collider.CompareTag("Light"))
                    Interact_with_Light(hit.collider.gameObject);
                else if (hit.collider.CompareTag("Drawer"))
                    Interact_with_Drawer(hit.collider.gameObject);
                else if (hit.collider.CompareTag("TV"))
                    Interact_with_TV(hit.collider.gameObject);
            }
            else if (prevObject != null)
            {
                // reset outline
                prevObject.GetComponent<Outline>().enabled = false;
                prevObject = null;
            }
        }

        DrawLine(rayStart, endPoint, currentColor);
    }

    private void DrawLine(Vector3 start, Vector3 end, Color color)
    {
        if (lineRenderer == null) return;

        lineRenderer.SetPosition(0, start);
        lineRenderer.SetPosition(1, end);

        lineRenderer.startColor = color;
        lineRenderer.endColor = color;
    }

    
    private void Interact_with_Light(GameObject light)
    {
        // enable outline
        light.GetComponent<Outline>().enabled = true;
        prevObject = light;
    }

    private void Interact_with_Drawer(GameObject drawer)
    {
        // enable outline
        GameObject drawerParent = drawer.transform.parent.parent.gameObject;
        drawerParent.GetComponent<Outline>().enabled = true;
        prevObject = drawerParent;
    }

    private void Interact_with_TV(GameObject tv)
    {
        // enable outline
        tv.GetComponent<Outline>().enabled = true;
        prevObject = tv;
    }
}