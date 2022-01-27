import time


class Trip:
    def __init__(self, to):
        self.to = to
        self.time = time.time()


class TripSchedule:

    def __init__(self):
        self.queue = {}
        self.disk_size = 5  # we have only 5 floors ;)

    def schedule_trip(self, trip):
        self.queue[trip.to] = trip

    def has_trip_scheduled(self):
        return len(self.queue) > 0

    def pop_trip(self, current_floor):
        # queue is empty
        if len(self.queue) == 0:
            return None
        if len(self.queue) == 1:
            next_floor = list(self.queue.values())[0].to
        else:
            next_floor = self.SCAN(list(self.queue.keys()), current_floor, "down")

        del (self.queue[next_floor])

        return next_floor

    def SCAN(self, arr, head, direction):
        """
        implementation of SCAN Algorithm,  source https://www.geeksforgeeks.org/scan-elevator-disk-scheduling-algorithms/
        props to divyesh072019
        """
        seek_count = 0
        down = []
        up = []
        seek_sequence = []

        # Appending end values
        # which has to be visited
        # before reversing the direction
        if direction == "down":
            down.append(0)
        elif direction == "up":
            up.append(self.disk_size - 1)

        for i in range(len(self.queue)):
            if arr[i] < head:
                down.append(arr[i])
            if arr[i] > head:
                up.append(arr[i])
        # Sorting down and up vectors
        down.sort()
        up.sort()
        # Run the while loop two times.
        # one by one scanning up
        # and down of the head
        run = 2
        while (run != 0):
            if direction == "down":
                for i in range(len(down) - 1, -1, -1):
                    cur_track = down[i]
                    # Appending current track to
                    # seek sequence
                    seek_sequence.append(cur_track)
                    # Calculate absolute distance
                    distance = abs(cur_track - head)
                    # Increase the total count
                    seek_count += distance
                    # Accessed track is now the new head
                    head = cur_track
                direction = "up"
            elif direction == "up":
                for i in range(len(up)):
                    cur_track = up[i]
                    # Appending current track to seek
                    # sequence
                    seek_sequence.append(cur_track)
                    # Calculate absolute distance
                    distance = abs(cur_track - head)
                    # Increase the total count
                    seek_count += distance
                    # Accessed track is now new head
                    head = cur_track
                direction = "down"
            run -= 1

        # print("Total number of seek operations =",
        #       seek_count)
        # print("Seek Sequence is")
        # for i in range(len(seek_sequence)):
        #     print(seek_sequence[i])

        return seek_sequence[0] if seek_sequence[0] != 0 else seek_sequence[1]
