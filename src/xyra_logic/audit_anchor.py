"""Offline write-once checkpoint export to a separately configured directory.

The caller MUST provide a genuinely independent custody boundary. Creating
files on the same host/disk does not constitute independent anchoring.
"""
import json
import os
import re

def export_anchor(audit,archive_dir,anchor_id):
    if not isinstance(anchor_id,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",anchor_id):
        raise ValueError("invalid anchor id")
    if not os.path.isdir(archive_dir):
        raise ValueError("archive directory unavailable")
    checkpoint=audit.checkpoint()
    payload=json.dumps({"anchor_id":anchor_id,"checkpoint":checkpoint},
                       sort_keys=True,separators=(",",":"))+"\n"
    path=os.path.join(archive_dir,anchor_id+".json")
    # Exclusive creation prevents accidental overwrite. The archive itself
    # needs independent access controls and retention enforcement.
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        try:os.unlink(path)
        except OSError:pass
        raise
    return path

def verify_anchor(audit,archive_dir,anchor_id):
    if not isinstance(anchor_id,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",anchor_id):
        return False
    try:
        with open(os.path.join(archive_dir,anchor_id+".json"),"rb") as f:
            raw=f.read(4097)
        if len(raw)>4096:
            return False
        record=json.loads(raw)
        return record.get("anchor_id")==anchor_id and audit.verify_checkpoint(record.get("checkpoint"))
    except (OSError,ValueError,TypeError,AttributeError):
        return False
