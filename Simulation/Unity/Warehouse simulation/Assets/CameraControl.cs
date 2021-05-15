using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraControl : MonoBehaviour
{
    public float rotateSpeed = 150f;
    public float moveSpeed = 50f;
    public float verticalSpeed = 25f;

    float rotationX = 0;
    float rotationY = 0;

    void Start()
    {
        rotationX = transform.localRotation.x;
        rotationY = transform.localRotation.y;

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

    }

    void Update()
    {
        if (!Cursor.visible)
        {
            float mouseX = Input.GetAxis("Mouse X") * rotateSpeed * Time.deltaTime;
            float mouseY = Input.GetAxis("Mouse Y") * rotateSpeed * Time.deltaTime;

            rotationX += mouseX;
            rotationY += mouseY;

            rotationY = Mathf.Clamp(rotationY, -85.0f, 85.0f);

            transform.localRotation = Quaternion.Euler(-rotationY, rotationX, 0);
        }

        if (Input.GetMouseButtonDown(0))
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))
        {
            Vector3 position2 = transform.position + transform.forward * moveSpeed * Time.deltaTime;
            transform.position = new Vector3(position2.x, transform.position.y, position2.z);
        }

        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))
        {
            transform.Translate(Vector3.left * moveSpeed * Time.deltaTime, Space.Self);
        }

        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow))
        {
            transform.Translate(Vector3.right * moveSpeed * Time.deltaTime, Space.Self);
        }

        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow))
        {
            Vector3 position2 = transform.position - transform.forward * moveSpeed * Time.deltaTime;
            transform.position = new Vector3(position2.x, transform.position.y, position2.z);
        }

        if (Input.GetKey(KeyCode.Space))
        {
            transform.Translate(Vector3.up * verticalSpeed * Time.deltaTime, Space.World);
        }
        else if (Input.GetKey(KeyCode.LeftShift))
        {
            if (transform.position.y > 2* verticalSpeed * Time.deltaTime)
            {
                transform.Translate(Vector3.down * verticalSpeed * Time.deltaTime, Space.World);
            }
        }

    }
}
