package basic;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;



public class main {
    public static void main(String[] args) {
    	int Flag = 1;
    	int flag = -Flag;
    	while(true) {
    	ServerSocket server = null;
    	
	    try {
		    server = new ServerSocket(22222);
		    
		    while(true) {
		    	
		    	/*
		    	Date : 21.09.11 
		    	Function : Ŭ���̾�Ʈ�κ��� �����ޱ�
		    	*/
		    	
			    Socket client = server.accept();
			    System.out.println(flag);
			    
			    BufferedReader br = new BufferedReader(
					    new InputStreamReader(
							    client.getInputStream(), "UTF-8"
					    )
			    );
			    
			    PrintWriter pw = new PrintWriter(client.getOutputStream(), true);
				
		    	/*
		    	Date : 21.09.13 
		    	Function : ������ ������ ������ Ŭ���̾�Ʈ���� END ��ȣ ������
		    	*/
			    
			    String message_1 = br.readLine();
			    if(message_1.trim().length()==0) {
			    	System.out.println("����");
				    pw.print("END");
				    pw.flush();
				    server.close();
				    break;
			    }
			    
			    System.out.println("name is : " + message_1);
			    
			    pw.print("Server  :"+message_1+" file receive");
			    pw.flush();
		
			    DataInputStream dis = new DataInputStream(client.getInputStream());
			    
		    	/*
		    	Date : 21.09.15 
		    	Function : ���� ������ Test, Train������ ������ �����ϱ�
		    	*/
			    
			    if (flag == -1) {
				    FileOutputStream fos = new FileOutputStream("C:\\Users\\jkjgo\\Desktop\\receiveimage\\train\\"+message_1+".jpg");
				    
				    
				    byte[] buffer = new byte[4096];
				    int len = 0;
				    while ((len = dis.read(buffer)) > 0) {
				        fos.write(buffer, 0, len);
				    }
				    fos.close();
				    flag = -flag;
			    }else {		    
				    FileOutputStream fos = new FileOutputStream("C:\\Users\\jkjgo\\Desktop\\receiveimage\\test\\"+message_1+".jpg");
				    
				    
				    byte[] buffer = new byte[4096];
				    int len = 0;
				    while ((len = dis.read(buffer)) > 0) {
				        fos.write(buffer, 0, len);
				    }
				    fos.close();
				    flag = -flag;
			    }
		    }//while�� ����
	    }
	    
	    catch(IOException e) {
			e.printStackTrace();
		}
    	}
	}
}
