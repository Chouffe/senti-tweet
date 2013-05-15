package client;

import twitter4j.*;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.util.HashMap;
import java.util.List;
import java.util.HashSet;
import java.util.Calendar;
import java.util.Date;
import java.text.SimpleDateFormat;

public class Main {

    public final static int NUMBER_OF_TWEETS = 20;
    public final static boolean INTERVAL = false;
    public final static int NUM_POINTS = 5;
    public final static long ONE_DAY = 86400000;

    public static void main(String[] args) {
        Twitter twitter = new TwitterFactory().getInstance();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        Date endDate = new Date();
        Date startDate = new Date(endDate.getTime() - ONE_DAY * NUM_POINTS);
        long interval = ONE_DAY;

        HashSet<String> tweetStorage = new HashSet<String>();
        try {
            SentimentAnalyser sa = new SentimentAnalyser();
            // Get the search term from the user.
            BufferedReader br = new BufferedReader(
                    new InputStreamReader(System.in)); 
            String search_term = "";
            try {
                // Search term
                System.out.println("What do you want to search for?");
                search_term = br.readLine();

            } catch(IOException e) {
                System.err.println("Could not read input.");
                return;
            }
            
            HashMap<String, Double> results = new HashMap<String, Double>();

            Date currentDate = startDate;
            for (int i = 0; i < NUM_POINTS; i++) {
                System.out.println("\nHarvesting tweets for "
                            + sdf.format(currentDate) + "\n");

                // Construct the query.
                Query query = new Query(search_term);
                query.setLang("en");
                query.setCount(NUMBER_OF_TWEETS);
                query.setUntil(sdf.format(currentDate));
                Date sinceDate = new Date(currentDate.getTime() - ONE_DAY);
                System.out.println(sdf.format(sinceDate));
                query.setSince(sdf.format(sinceDate));
                QueryResult result;
                result = twitter.search(query);

                float score = 0;
                // Iterate over the tweets from the query result.
                List<Status> tweets = result.getTweets();
                for (Status tweet : tweets) {
                    if(tweet.isRetweet()){
                        tweet = tweet.getRetweetedStatus();
                    }
                    if(tweetStorage.contains(tweet.getText())){
                        continue;
                    }
                    //Add the text to our hashset
                    tweetStorage.add(tweet.getText());

                    int followers = tweet.getUser().getFollowersCount();
                    long retweets = tweet.getRetweetCount();

                    //Calculate the weight of the tweet. 
                    //Great emphasis on retweets.
                    double weight = ((followers != 0) ? (Math.log10(followers))
                            : 0) + 3 * ((retweets != 0) ? (Math.log10(retweets))
                            : 0);
                    weight /= 2;

                    float tmpScore = sa.analyse(tweet.getText());
                    tmpScore *= weight;
                    score += tmpScore;
                }

                System.out.println("Total score of the term " + search_term + 
                        " is " + score);
                results.put(sdf.format(currentDate), new Double(score));
                BufferedWriter fp = new BufferedWriter(new FileWriter("plot-data.txt"));
                for(String date : results.keySet()) {
                	fp.write(date+";"+results.get(date)+"\n");
                }
                fp.close();

                currentDate = new Date(currentDate.getTime() + interval);
            }
            
            System.exit(0);
        } catch (TwitterException te) {
            te.printStackTrace();
            System.out.println("Failed to search tweets: " + te.getMessage());
            System.exit(-1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
