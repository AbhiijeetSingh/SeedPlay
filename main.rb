require "uri"
require "net/http"
require "openssl"
require "nokogiri"
require "tty-prompt"

#replace with your own url
$base_url = "https://username:password@psb60880.seedbox.io/files/"

def parser(response)
    # parse the response and return a zipped hash of links
    result = Nokogiri::HTML(response.body)
    texts = result.css("a").map{|a| a.text}
    links = result.css("a").map { |link| link["href"] }
    zipped_links = Hash[texts.zip(links)]
    inquiry zipped_links
end

def get_data(url)
    # request data from url using appropriate authentication credentials
    # and pass the response to the parser
    uri = URI(url)
    @http = Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme, verify_mode: OpenSSL::SSL::VERIFY_NONE) do |http|
        request = Net::HTTP::Get.new(uri.request_uri)
        # replace username and password with your own
        request.basic_auth("username", "password")
        response = http.request(request)
        parser(response)
    end 
end

def inquiry(hashed_links)
    # prompt user to select a link from the hash keys
    # if the user selects a link, play the link in mpv
    # if the user selects a folder, recursively call the get_data method
    prompt = TTY::Prompt.new
    choice = prompt.select("What do you want to play?", hashed_links.keys, per_page: 30)
    choice = hashed_links[choice]
    $base_url = $base_url + choice 
    if choice.end_with? "/"
        get_data($base_url)
    else
        exec("mpv #{$base_url}")
    end
end

def main
    puts "Seedplay"
    zipped_links = get_data($base_url)
end

main