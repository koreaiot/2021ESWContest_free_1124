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
		    	Function : 클라이언트로부터 사진받기
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
		    	Function : 마지막 사진을 받으면 클라이언트에게 END 신호 보내기
		    	*/
			    
			    String message_1 = br.readLine();
			    if(message_1.trim().length()==0) {
			    	System.out.println("들어옴");
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
		    	Function : 받은 사진을 Test, Train셋으로 나누어 저장하기
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
		    }//while문 종료
	    }
	    
	    catch(IOException e) {
			e.printStackTrace();
		}
    	}
	}
}
