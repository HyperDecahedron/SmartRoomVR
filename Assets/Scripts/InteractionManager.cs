using UnityEngine;

public class InteractionManager : MonoBehaviour
{
    // Room objects
    public GameObject tv;

    private float cooldownTime = 0.5f;

    private float lastTVTime = -Mathf.Infinity;
    private float lastLightTime = -Mathf.Infinity;
    private float lastDrawerTime = -Mathf.Infinity;

    public void SetTV()
    {
        // Cooldown check
        if (Time.time < lastTVTime + cooldownTime)
            return;

        lastTVTime = Time.time;

        if (tv == null || tv.transform.childCount == 0)
            return;

        GameObject firstChild = tv.transform.GetChild(0).gameObject;
        firstChild.SetActive(!firstChild.activeSelf);
    }

    public void SetLight(GameObject detected_lamp)
    {
        // Cooldown check
        if (Time.time < lastLightTime + cooldownTime)
            return;

        lastLightTime = Time.time;

        if (detected_lamp == null || detected_lamp.transform.childCount == 0)
            return;

        GameObject firstChild = detected_lamp.transform.GetChild(0).gameObject;
        firstChild.SetActive(!firstChild.activeSelf);
    }

    public void SetDrawer(GameObject detected_drawer)
    {
        // Cooldown check
        if (Time.time < lastDrawerTime + cooldownTime)
            return;

        lastDrawerTime = Time.time;

        if (detected_drawer == null || detected_drawer.transform.childCount == 0)
            return;

        GameObject firstChild = detected_drawer.transform.GetChild(0).gameObject;

        Animator animator = firstChild.GetComponent<Animator>();
        if (animator == null)
            return;

        // Get current value and toggle it
        bool isOpen = animator.GetBool("IsOpen");
        animator.SetBool("IsOpen", !isOpen);
    }
}