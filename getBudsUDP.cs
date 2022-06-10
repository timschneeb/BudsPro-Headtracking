using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/*
 * Modified from........
 *
 * Author: Hyung-il Kim
 * M.S. Student, KAIST UVR Lab.
 * 
 * Receives rotation vector as quaternion, by UDP comm.
 * x, y, z, w
 * 
 * - Recenter rotation using space bar
*/

using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class getBudsUDP : MonoBehaviour {

	// receiving Thread
	Thread receiveThread;

    // udpclient object
    UdpClient client;

    // port number
    public String TARGET_IP = "127.0.0.1";
    public int TARGET_PORT = 12563;

    public int RECEIVING_PORT = 12562; // define > init

    public float ID = -1;
    public Vector3 gyro = new Vector3(.0f,.0f,.0f);
    public Vector3 acc = new Vector3(.0f,.0f,.0f);
    public Vector4 rot = new Vector4(.0f,.0f,.0f,.0f);

    public int sent_num = 0;


    
    public getBudsUDP(int port){
        this.RECEIVING_PORT = port;
    }

    IEnumerator Start()
    {
        Debug.Log("UDPSendReceive: Starting");
        this.init();

        yield return new WaitForSeconds(1.0f);

    }
    void Update()
    {
        if (Input.GetKeyDown("space"))
        {
            print("space key was pressed");
            sent_num += 1;

            UdpClient udpClient = new UdpClient(TARGET_IP, TARGET_PORT);
            Debug.Log("UDPSendReceive: sending"+TARGET_IP+":"+TARGET_PORT);
            

            byte[] sendBytes2 = ConvertDoubleToByte(new double[]{sent_num, sent_num*0.3, sent_num*0.5});
            
            try{
                // Byte[] sendBytes = Encoding.ASCII.GetBytes("sending test"+sent_num);
                // udpClient.Send(sendBytes, sendBytes.Length);


                udpClient.Send(sendBytes2, sendBytes2.Length);
            }
            catch ( Exception e ){
                Console.WriteLine( e.ToString());
            }
        }
        transform.eulerAngles = new Vector3(rot.x,rot.y,rot.z);
        // transform.Rotate(rot, Space.Self);
        // Debug.Log("UDPSendReceive: receiveThread background=" + receiveThread.IsBackground);
    }

    // OnDestroy
    public void OnDestroy()
    {
        receiveThread.Abort();
        client.Close();
        Debug.Log("UDPSendReceive: OnDestroy");
    }

	// init
	private void init()
	{		
        // Define local endpoint (where messages are received).
        // Create a new thread for the reception create incoming messages.
		receiveThread = new Thread(new ThreadStart(ReceiveData));
		receiveThread.IsBackground = false;
		receiveThread.Start();
    }



    public static float[] ConvertByteToFloat(byte[] array)
    {
        float[] floatArr = new float[10];
        for (int i = 0; i < floatArr.Length; i++)
        {
            // if (BitConverter.IsLittleEndian)
            // {
            //     Array.Reverse(array, i * 4, 4);
            // }
            floatArr[i] = BitConverter.ToSingle(array, i * 4);
        }
        return floatArr;
    }
    public static byte[] ConvertDoubleToByte(double[] array)
    {
        byte[] byte_arr = new byte[8*array.Length];
        for (int i = 0; i < array.Length; i++)
        {
            byte[] bytes = BitConverter.GetBytes( array[i]); 
            Array.Copy(bytes, 0, byte_arr , 8*i, bytes.Length);
        }
        return byte_arr;
    }



	// receive thread
	private void ReceiveData()
	{
		//char[] delim = {'#'};
		
		client = new UdpClient(RECEIVING_PORT);
        Debug.Log("UDPSendReceive: listening at port.... " + RECEIVING_PORT);
		while (true)
		{
			try
			{
				// Bytes received.
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                // Debug.Log("UDPSendReceive: get input");
                byte[] data = client.Receive(ref anyIP);
                String receive_str = Encoding.UTF8.GetString(data);
                // Debug.Log("UDPSendReceive: " + receive_str);

                string[] subs = receive_str.Split(',');
                rot.x = float.Parse(subs[0]);
                rot.y = float.Parse(subs[1]);
                rot.z = float.Parse(subs[2]);
                // rot.w = float.Parse(subs[3]);

                // Array.Reverse(data, 0, 4);
                // int num_of_input_set = BitConverter.ToInt16(data, 0);
                // Debug.Log("UDPSendReceive: num_of_input_set:" + num_of_input_set);
                



                // for (int i = 0; i < num_of_input_set; i++)
                // {
                //     byte[] oneset_arr = new byte[52];

                //     Array.Copy(data, 4+52*i, oneset_arr, 0, 52);
                //     // convert received byte array to float array.
                //     float[] values = ConvertByteToFloat(oneset_arr); // Gx,Gy,Gz, ACCx,ACCy,ACCz, ROTx,ROTy,ROTz,ROTw

                //     // Array.Reverse(oneset_arr, 40, 8);
                //     // Array.Reverse(oneset_arr, 48, 4);

                //     double device_time = BitConverter.ToInt64(oneset_arr, 40);
                //     int dev_id_int = BitConverter.ToInt16(oneset_arr, 48);
                //     Debug.Log("UDPSendReceive: device_time:" + device_time);
                //     Debug.Log("UDPSendReceive: dev_id:" + dev_id_int);

                //     // these values can be modified..
                //     gyro[0] = values[0];
                //     gyro[1] = values[1];
                //     gyro[2] = values[2];

                //     acc[0] = values[3];
                //     acc[1] = values[4];
                //     acc[2] = values[5];

                //     rot.x = values[6];
                //     rot.y = values[7];
                //     rot.z = values[8];
                //     rot.w = values[9];
                //     Debug.Log("UDPSendReceive: sensorval:" + values[0]+","+ values[1]+","+ values[2]+"|"+
                //         values[3] + "," + values[4] + "," + values[5]+"|"+
                //         values[6] + "," + values[7] + "," + values[8] + "," + values[9]);


                // }
                

            }
            catch (Exception err)
			{
				print(err.ToString());
			}
		}
	}

}