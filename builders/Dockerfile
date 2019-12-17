# We need a gcc docker image
FROM gcc

# Copy the polling scrip
COPY poll.sh /usr/local/bin/

# Copy polling service
COPY pollservice /etc/init.d/

# Add rights to pollservice
RUN chmod +x /etc/init.d/pollservice

# Configure service auto-start
#CMD ["update-rc.d", "pollservice", "defaults"]

# Start polling service
CMD ["/usr/local/bin/poll.sh", "/var/run/poll", "py", "5", "&"]
