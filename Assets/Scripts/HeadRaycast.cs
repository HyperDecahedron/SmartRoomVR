using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class HeadRaycast : MonoBehaviour
{
    [SerializeField] private InteractionManager interactionManager;
    [SerializeField] private GameObject pointer;
    [SerializeField] private LayerMask raycastMask;

    [SerializeField] private Material white_mat;
    [SerializeField] private Material blue_mat;

    private float maxDistance = 8f;
    private float yOffset = -0.1f;
    private LineRenderer lineRenderer;
    private Renderer pointerRenderer;

    private readonly Color validHitColor = new Color32(0x00, 0xFF, 0xE3, 0xFF);
    private readonly Color defaultColor = new Color32(0xFF, 0xFF, 0xFF, 150);

    private void Awake()
    {
        lineRenderer = GetComponent<LineRenderer>();
        if (lineRenderer != null)
        {
            lineRenderer.positionCount = 2;
        }

        pointerRenderer = pointer.GetComponent<Renderer>();

        // Ignore objects in the "Ignore Raycast" layer
        raycastMask = ~LayerMask.GetMask("Ignore Raycast");
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
        Material currentMaterial = white_mat;

        if (Physics.Raycast(rayStart, rayDirection, out RaycastHit hit, maxDistance, raycastMask))
        {
            endPoint = hit.point;

            if (hit.collider.CompareTag("Light") ||
                hit.collider.CompareTag("Drawer") ||
                hit.collider.CompareTag("TV"))
            {
                currentColor = validHitColor;
                currentMaterial = blue_mat;
            }
        }

        // set pointer at the end of the line
        pointer.transform.position = endPoint;
        if (pointerRenderer != null)
        {
            pointerRenderer.material = currentMaterial;
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
}