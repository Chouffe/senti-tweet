package client;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;

/**
 * Contact the Python sentiment analyser and return the analysis
 * @author calixtebonsart
 *
 */
public class SentimentAnalyser {
	private Socket client;
	
	/**
	 * Creates socket to contact Python server
	 * @param host Machine hosting the Python server (usually localhost)
	 * @param port Port of the host
	 * @throws UnknownHostException usually when server is down
	 * @throws IOException
	 */
	public SentimentAnalyser(String host, int port) throws UnknownHostException, IOException {
		client = new Socket(host, port);
	}
	
	/**
	 * Starts client on localhost:12800
	 * @throws UnknownHostException usually when server is down
	 * @throws IOException
	 */
	public SentimentAnalyser() throws UnknownHostException, IOException {
		this("localhost", 12800);
	}
	
	/**
	 * Analyse the sentiment of a tweet
	 * @param tweet Tweet to analyse
	 * @return -1, 0 or 1, result of the sentiment analysis of the tweet
	 * @throws IOException
	 */
	public int analyse(String tweet) throws IOException {
		DataInputStream inputStream = new DataInputStream(client.getInputStream());
		DataOutputStream outputStream = new DataOutputStream(client.getOutputStream());
		outputStream.write(ByteBuffer.allocate(4).putInt(tweet.length()).array());
		outputStream.writeUTF(tweet);
		byte[] res = new byte[4];
		inputStream.read(res);
		int c = ByteBuffer.wrap(res).getInt();
		return c-1;
	}
	
	public static void main(String[] args) throws UnknownHostException, IOException {
		SentimentAnalyser sa = new SentimentAnalyser();
		System.out.println(sa.analyse("I hate Google !"));
		System.out.println(sa.analyse("I love Google ! #lol"));
		System.out.println(sa.analyse("I hate Google ! #lol #lol"));
		System.out.println(sa.analyse("I love Google ! #lol #lol #lol #lol"));
		System.out.println(sa.analyse("I hate Google ! #lol #lol #lol #lol #lol #lol"));
		System.out.println(sa.analyse("I love Google ! #lol #lol #lol #lol #lol #lol #lol #lol"));
	}
}
