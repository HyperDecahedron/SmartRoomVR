using UnityEngine;

public class ChangeTV : MonoBehaviour
{
    public Texture texture1;
    public Texture texture2;

    private Renderer objectRenderer;
    private bool showingFirst = true;

    void Start()
    {
        objectRenderer = GetComponent<Renderer>();
        objectRenderer.material.mainTexture = texture1;

        gameObject.SetActive(false);

        // Repeat the texture change every 2 seconds
        InvokeRepeating(nameof(ChangeTexture), 2f, 2f);
    }

    void ChangeTexture()
    {
        showingFirst = !showingFirst;

        if (showingFirst)
        {
            objectRenderer.material.mainTexture = texture1;
        }
        else
        {
            objectRenderer.material.mainTexture = texture2;
        }
    }
}