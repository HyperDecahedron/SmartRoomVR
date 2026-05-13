using System.Collections.Concurrent;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using System.Globalization;

public class TongueInterface : MonoBehaviour
{
    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isRunning = true;
    private InteractionManager interactionManager;

    public int press_threshold = 50;
    public float triggerCooldown = 1f;

    public float currentJitter = 0f;
    public int[] currentPressure = new int[3];

    private float lastTriggerTime = -999f;

    public struct UdpData
    {
        public float Jitter;
        public int[] Pressure;

        public UdpData(float jitter, int[] pressure)
        {
            Jitter = jitter;
            Pressure = pressure;
        }
    }

    public event Action<UdpData> OnDataReceived;

    private ConcurrentQueue<UdpData> mainThreadQueue = new ConcurrentQueue<UdpData>();

    void Start()
    {
        interactionManager = GameObject.FindWithTag("InteractionManager").GetComponent<InteractionManager>();

        Debug.Log("tongue listener started");
        try
        {
            udpClient = new UdpClient(5052);
            receiveThread = new Thread(ReceiveData);
            receiveThread.IsBackground = true;
            receiveThread.Start();
        }
        catch (Exception e)
        {
            Debug.LogError("Failed to start UDP: " + e.Message);
        }
    }

    void ReceiveData()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 5052);

        while (isRunning)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string message = Encoding.UTF8.GetString(data).Trim();

                string[] parts = message.Split(',');

                //Debug.Log(message);

                if (parts.Length == 4)
                {
                    float jitter = float.Parse(parts[0], CultureInfo.InvariantCulture);
                    jitter = Mathf.Clamp(jitter, 0f, 1f);

                    int p0 = int.Parse(parts[1]);
                    int p1 = int.Parse(parts[2]);
                    int p2 = int.Parse(parts[3]);

                    UdpData udpData = new UdpData(jitter, new int[] { p0, p1, p2 });
                    mainThreadQueue.Enqueue(udpData);
                }
                else
                {
                    Debug.LogWarning("Invalid UDP message format: " + message);
                }
            }
            catch (SocketException)
            {
                break;
            }
            catch (Exception ex)
            {
                Debug.LogError("UDP receive error: " + ex.Message);
            }
        }
    }

    void Update()
    {
        while (mainThreadQueue.TryDequeue(out UdpData data))
        {
            currentJitter = data.Jitter;
            currentPressure = data.Pressure;

            OnDataReceived?.Invoke(data);

            bool pressureOverThreshold =
                data.Pressure[0] > press_threshold ||
                data.Pressure[1] > press_threshold ||
                data.Pressure[2] > press_threshold;

            bool cooldownFinished = Time.time >= lastTriggerTime + triggerCooldown;

            if (pressureOverThreshold && cooldownFinished)
            {
                if (interactionManager != null)
                {
                    interactionManager.SelectObject();
                    lastTriggerTime = Time.time;
                }
                else
                {
                    Debug.LogWarning("InteractionManager is not assigned.");
                }
            }
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        udpClient?.Close();
        receiveThread?.Join();
    }
}