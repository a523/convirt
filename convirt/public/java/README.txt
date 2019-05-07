How to create a Signed JAR file 
-------------------------------

1: Compile the Applet

javac AppletRunner.java

2: Make a JAR File

jar cvf AppletRunner.jar AppletRunner.class

3: Generate Keys

A JAR file is signed with the private key of the creator of the JAR file and the signature is verified by the recipient of the JAR file with the public key in the pair. The certificate is a statement from the owner of the private key that the public key in the pair has a particular value so the person using the public key can be assured the public key is authentic. Public and private keys must already exist in the keystore database before jarsigner can be used to sign or verify the signature on a JAR file.

Create a keystore database named compstore that has an entry for a newly generated public and private key pair with the public key in a certificate using the keytool command.

keytool -genkey -alias signFiles -keystore compstore 
	-keypass kpi135 -dname "cn=jones" 
	-storepass ab987c

This keytool -genkey command invocation generates a key pair that is identified by the alias signFiles. Subsequent keytool command invocations use this alias and the key password (-keypass kpi135) to access the private key in the generated pair.

The generated key pair is stored in a keystore database called compstore (-keystore compstore) in the current directory, and accessed with the compstore password (-storepass ab987c).

The -dname "cn=jones" option specifies an X.500 Distinguished Name with a commonName (cn) value. X.500 Distinguished Names identify entities for X.509 certificates. 

4: Sign the JAR File

JAR Signer is a command line tool for signing and verifying the signature on JAR files. 

jarsigner -keystore compstore -storepass ab987c 
        -keypass kpi135 
	-signedjar 
	SAppletRunner.jar AppletRunner.jar signFiles

The -storepass ab987c and -keystore compstore options specify the keystore database and password where the private key for signing the JAR file is stored. The -keypass kpi135 option is the password to the private key, SAppletRunner.jar is the name of the signed JAR file, and signFiles is the alias to the private key. jarsigner extracts the certificate from the keystore whose entry is signFiles and attaches it to the generated signature of the signed JAR file.

5: Copy the signed JAR file to convirt directory

Copy the newly created SAppletRunner.jar to the src/convirt/web/convirt/convirt/public/jar directory under convirt directory

cp SAppletRunner.jar src/convirt/web/convirt/convirt/public/jar




courtesy : http://java.sun.com/developer/onlineTraining/Programming/JDCBook/signed.html
 
