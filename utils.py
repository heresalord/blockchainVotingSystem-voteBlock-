import datetime

def time_remaining(start_time, vote_duration):
    remaining_time = max(vote_duration - int(time.time() - start_time), 0)

    days = remaining_time // (24 * 3600)
    remaining_time %= (24 * 3600)
    hours = remaining_time // 3600
    remaining_time %= 3600
    minutes = remaining_time // 60
    remaining_time %= 60
    seconds = remaining_time

    return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

def filter_data_based_on_time(blockchain, hours):
    filtered_data = []
    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
    for block in blockchain.chain:
        if block.timestamp >= cutoff_time:
            filtered_data.append(block)
    return filtered_data
