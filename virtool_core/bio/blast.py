
class BLAST:

    def __init__(self, db, settings: dict, analysis_id: str, sequence_index: int, rid: str):
        self.db = db
        self.settings = settings
        self.analysis_id = analysis_id
        self.sequence_index = sequence_index
        self.rid = rid
        self.error = None
        self.interval = 3
        self.ready = False
        self.result = None

    async def remove(self):
        """
        Remove the BLAST result from the analysis document.

        """
        await remove_nuvs_blast(self.db, self.analysis_id, self.sequence_index)

    async def sleep(self):
        """
        Sleep for the current interval and increase the interval by 5 seconds after sleeping.

        """
        await asyncio.sleep(self.interval)
        self.interval += 5

    async def update(self, ready: bool, result: Union[None, dict], error: Union[None, str]) -> Tuple[dict, dict]:
        """
        Update the BLAST data. Returns the BLAST data and the complete analysis document.

        :param ready: indicates whether the BLAST request is complete
        :param result: the formatted result of a successful BLAST request
        :param error: and error message to add to the BLAST record
        :return: the BLAST data and the complete analysis document

        """
        self.result = result

        if ready is None:
            self.ready = await virtool.bio.check_rid(self.settings, self.rid)
        else:
            self.ready = ready

        data = {
            "error": error,
            "interval": self.interval,
            "last_checked_at": virtool.utils.timestamp(),
            "rid": self.rid,
            "ready": ready,
            "result": self.result
        }

        document = await self.db.analyses.find_one_and_update({
            "_id": self.analysis_id,
            "results.index": self.sequence_index
        }, {
            "$set": {
                "results.$.blast": data,
                "updated_at": virtool.utils.timestamp()
            }
        })

        return data, document