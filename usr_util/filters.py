import time


def time_str(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(t) + 3600 * 8))


def pay_status(t):
    d = {
        0: '<span class="text-danger">未支付</span>',
        1: '<span class="text-success">已支付</span>',
    }
    return d.get(t, '待处理')


def bill_mode(t):
    d = {
        0: '金额',
        1: '点数',
    }
    return d.get(t, '待处理')


filters = {
    'time_str': time_str,
    'pay_status': pay_status,
    'bill_mode': bill_mode,
}
