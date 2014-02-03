/*
 * Web Server
 *
 * A simple web server that serves a static page.
 *
*/

#include <Ethernet.h>

/* Ethernet device MAC address (modify this) */
byte mac[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06 };

/* The server's IP address  */
IPAddress ip(192, 168, 1, 225);

/* Create an EthernetServer object on port 80 */
EthernetServer server(80);

void setup()
{
	Serial.begin(9600);
	Ethernet.begin(mac, ip);
	server.begin();
	Serial.print("Server running on ");
	Serial.println(Ethernet.localIP());
}

void loop()
{
	/* Listen for incoming connections */
	EthernetClient client = server.available();

	if (client)
	{
		Serial.println("Client connected.");

		/* Print the client's request */
		while (client.available())
		{
			char c = client.read();
			Serial.write(c);
		}

		/* Send a response */
		client.println("HTTP/1.1 200 OK");
		client.println("Content-Type: text/html");
		client.println("Connection: close");
		client.println();
		client.println("<!doctype html>");
		client.println("<html>");
		client.println("<h1>Hello world</h1>");
		client.println("</html>");

		/* Give the browser time to receive the data */
		delay(1);

		/* Close the connection */
		client.stop();
		Serial.println("Client disconnected.");
	}
}
