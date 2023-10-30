from pydantic import BaseModel


class TCPConnection(BaseModel):
    srv_count: float = -0.08998232044471013
    serror_rate: float = -0.05717965923512565
    srv_serror_rate: float = -0.0669275410664081
    rerror_rate: float = -0.24424509125779062
    srv_rerror_rate: float = -0.24681110501029294
    same_srv_rate: float = 0.15547767515584282
    diff_srv_rate: float = -0.1547286301259249
    srv_diff_host_rate: float = 0.31192910302625787
    dst_host_count: float = 0.6151565022315362
    dst_host_srv_count: float = 0.6088064982567516
    dst_host_same_srv_rate: float = 0.5074166807809835
    dst_host_diff_srv_rate: float = -0.31360578470756284
    dst_host_same_src_port_rate: float = -0.4782746784956824
    dst_host_srv_diff_host_rate: float = -0.08374494180592064
    dst_host_serror_rate: float = -0.07210689160611908
    dst_host_srv_serror_rate: float = -0.0691924142907873
    dst_host_rerror_rate: float = -0.25692908263833586
    dst_host_srv_rerror_rate: float = -0.2553004561346714
