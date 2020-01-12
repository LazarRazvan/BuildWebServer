# We need a gcc docker image
FROM rsmmr/clang	

# Copy polling scrip and build script
COPY poll.sh /usr/local/bin/
COPY build.sh /usr/local/bin/

# Create logs directory
RUN mkdir -p /var/log/poll
RUN touch /var/log/poll/messages

# Create sources directory
RUN mkdir -p /var/run/poll_src

# Create results directory
RUN mkdir -p /var/run/poll_res

# Start polling service
CMD ["/usr/local/bin/poll.sh", "/var/run/poll_src", "/var/run/poll_res", "/var/log/poll/messages", "zip", "10", "&"]
