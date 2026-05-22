using UnityEngine;
using DoorScript;
using System;

public class InteractionManager : MonoBehaviour
{
    [NonSerialized] public GameObject current_object = null;

    private AudioSource audio; 

    private void Start()
    {
        audio = GetComponent<AudioSource>();
    }

    public void SelectObject()
    {
        if (current_object != null)
        {
            if(current_object.tag == "Light")
            {
                SetLight();
            }
            else if (current_object.tag == "TV")
            {
                SetTV();
            }
            else if(current_object.tag == "Drawer")
            {
                SetDrawer();
            }
            else if (current_object.tag == "Door")
            {
                SetDoor();
            }
        }
    }

    public void SetTV()
    {
        if (current_object == null)
            return;
            
        GameObject firstChild = current_object.transform.GetChild(0).gameObject;
        firstChild.SetActive(!firstChild.activeSelf);

        if (audio != null) {
            audio.Play();
        }
    }

    public void SetLight()
    {
        if (current_object == null || current_object.transform.childCount == 0)
            return;

        Debug.Log("called set light");
        GameObject firstChild = current_object.transform.GetChild(0).gameObject;
        firstChild.SetActive(!firstChild.activeSelf);

        if (audio != null)
        {
            audio.Play();
        }
    }

    public void SetDrawer()
    {
        if (current_object == null)
            return;

        GameObject parent = current_object.transform.parent.gameObject;

        Animator animator = parent.GetComponent<Animator>();
        if (animator == null)
            return;

        // Get current value and toggle it
        bool isOpen = animator.GetBool("IsOpen");
        animator.SetBool("IsOpen", !isOpen);

        if (audio != null)
        {
            audio.Play();
        }
    }

    public void SetDoor()
    {
        if (current_object == null)
            return;

        DoorScript.Door door_component = current_object.GetComponent<DoorScript.Door>();
        door_component.open = !door_component.open;

        if (audio != null)
        {
            audio.Play();
        }
    }
}