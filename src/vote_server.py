"""
A wrapper class for ResDBORM to manage Vote data records,
with some helper functions and better error handling.
"""
from resdb_orm import ResDBORM
from dataclasses import asdict
import logging
from returns.maybe import Maybe, Some, Nothing
from typing import Any

from .datatype import Vote

class VoteServer:
    def __init__(self, config_path: str, log_path: str | None = None) -> None:
        self.db = ResDBORM(config_path)
        self.record_ids: set[str] = set()
        self._log_path = log_path
        
        if log_path is not None:
            self.log_file = open(log_path, "a")
            self._load_from_log()
        
    def __del__(self) -> None:
        self.delete_all()
        if self._log_path is not None:
            self.log_file.close()
        
    def _load_from_log(self) -> None:
        """load record ids from the log file if it is in the DB
        """
        assert self._log_path is not None
        with open(self._log_path, "r") as f:
            for line in f:
                record_id = line.strip()
                match self.read(record_id):
                    case Some(_):
                        self.record_ids.add(record_id)
                    case Nothing:
                        pass
        
        
    def create(self, vote: Vote) -> Maybe[str]:
        """create a single vote record in the DB

        Args:
            vote (Vote): the vote record to be created

        Returns:
            Maybe[str]: the record id if successful, Nothing otherwise
        """
        try:
            response = self.db.create(asdict(vote))
        except Exception as e:
            logging.warning(f"VoteServer.create: request error {e}")
            return Nothing
        
        if not isinstance(response, str):
            if isinstance(response, dict) and "status" in response:
                logging.warning(f"VoteServer.create: {response['status']}")
            else:
                logging.warning("VoteServer.create: unknown error from ResDB.")
            return Nothing
            
        
        self.record_ids.add(response)
        
        if self._log_path is not None:
            self.log_file.write(f"{response}\n")
        return Some(response)
    
    def create_all(self, votes: list[Vote]) -> list[Maybe[str]]:
        """create multiple vote records in the DB

        Args:
            votes (list[Vote]): a list of vote records to be created

        Returns:
            list[str]: a list of record ids
        """
        return list(map(self.create, votes))
        
    def read(self, record_id: str) -> Maybe[Vote]:
        """read a single vote record from the DB

        Args:
            record_id (str): the record id to be read

        Returns:
            Maybe[Vote]: the vote record if successful, Nothing otherwise
        """
        try:
            response = self.db.read(record_id)
        except Exception as e:
            logging.warning(f"VoteServer.read: request error {e}")
            return Nothing
        
        if not isinstance(response, dict):
            if isinstance(response, str):
                logging.warning(f"VoteServer.read: {response}")
            else:
                logging.warning("VoteServer.read: unknown error from ResDB.")
            return Nothing
        
        try:
            assert record_id == response["id"]
            vote_data = response["data"]
        except KeyError as e:
            logging.warning(f"VoteServer.read: KeyError {e}")
            return Nothing
        return Some(Vote(**vote_data))
    
    def read_all(self) -> list[Vote]:
        votes = [self.read(rid).unwrap() for rid in self.record_ids]
        return votes
    
    def db_read_all(self) -> Any:
        """read all data records from the DB, no matter if it is created by this server or not

        Returns:
            list[Vote]: a list of Vote objects
        """
        try:
            response = self.db.read_all()
        except Exception as e:
            logging.warning(e)
            return None
        
        return response
        

    def delete_all(self):
        """delete all data records managed by this server
        """
        
        for rid in self.record_ids:
            response = self.db.delete(rid)
            if isinstance(response, dict) and "status" in response and response["status"] != "delete successful":
                logging.warning(response["status"])
            
    def db_delete_all(self):
        """delete all data records in the DB"""
        try:
            response = self.db.read_all()
        except Exception as e:
            logging.warning(e)
            return
        
        for record in response:
            self.db.delete(record["id"])
        
