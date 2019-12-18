# We need a gcc docker image
FROM rsmmr/clang	

# Copy the polling scrip
COPY poll.sh /usr/local/bin/

# Create logs directory
RUN mkdir -p /var/log/poll

# Create sources directory
RUN mkdir -p /var/run/poll

# Start polling service
CMD ["/usr/local/bin/poll.sh", "/var/run/poll", "py", "5", "&"]
