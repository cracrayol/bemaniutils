# vim: set fileencoding=utf-8
from typing import Dict, List, Optional

from bemani.backend.base import Base
from bemani.backend.core import CoreHandler, CardManagerHandler, PASELIHandler
from bemani.common import DBConstants, GameConstants, ValidatedDict
from bemani.data import Score, UserID
from bemani.protocol import Node


class JubeatBase(CoreHandler, CardManagerHandler, PASELIHandler, Base):
    """
    Base game class for all Jubeat versions. Handles common functionality for getting
    profiles based on refid, creating new profiles, looking up and saving scores.
    """

    game = GameConstants.JUBEAT

    GAME_FLAG_BIT_PLAYED = 0x1
    GAME_FLAG_BIT_CLEARED = 0x2
    GAME_FLAG_BIT_FULL_COMBO = 0x4
    GAME_FLAG_BIT_EXCELLENT = 0x8
    GAME_FLAG_BIT_NEARLY_FULL_COMBO = 0x10
    GAME_FLAG_BIT_NEARLY_EXCELLENT = 0x20
    GAME_FLAG_BIT_NO_GRAY = 0x40
    GAME_FLAG_BIT_NO_YELLOW = 0x80

    PLAY_MEDAL_FAILED = DBConstants.JUBEAT_PLAY_MEDAL_FAILED
    PLAY_MEDAL_CLEARED = DBConstants.JUBEAT_PLAY_MEDAL_CLEARED
    PLAY_MEDAL_NEARLY_FULL_COMBO = DBConstants.JUBEAT_PLAY_MEDAL_NEARLY_FULL_COMBO
    PLAY_MEDAL_FULL_COMBO = DBConstants.JUBEAT_PLAY_MEDAL_FULL_COMBO
    PLAY_MEDAL_NEARLY_EXCELLENT = DBConstants.JUBEAT_PLAY_MEDAL_NEARLY_EXCELLENT
    PLAY_MEDAL_EXCELLENT = DBConstants.JUBEAT_PLAY_MEDAL_EXCELLENT

    CHART_TYPE_BASIC = 0
    CHART_TYPE_ADVANCED = 1
    CHART_TYPE_EXTREME = 2

    def previous_version(self) -> Optional['JubeatBase']:
        """
        Returns the previous version of the game, based on this game. Should
        be overridden.
        """
        return None

    def put_profile(self, userid: UserID, profile: ValidatedDict) -> None:
        """
        Save a new profile for this user given a game/version. Overrides but calls
        the same functionality in Base, to ensure we don't save calculated values.

        Parameters:
            userid - The user ID we are saving the profile for.
            profile - A dictionary that should be looked up later using get_profile.
        """
        if 'has_old_version' in profile:
            del profile['has_old_version']
        super().put_profile(userid, profile)

    def format_profile(self, userid: UserID, profile: ValidatedDict) -> Node:
        """
        Base handler for a profile. Given a userid and a profile dictionary,
        return a Node representing a profile. Should be overridden.
        """
        return Node.void('gametop')

    def format_scores(self, userid: UserID, profile: ValidatedDict, scores: List[Score]) -> Node:
        """
        Base handler for a score list. Given a userid, profile and a score list,
        return a Node representing a score list. Should be overridden.
        """
        return Node.void('gametop')

    def unformat_profile(self, userid: UserID, request: Node, oldprofile: ValidatedDict) -> ValidatedDict:
        """
        Base handler for profile parsing. Given a request and an old profile,
        return a new profile that's been updated with the contents of the request.
        Should be overridden.
        """
        return oldprofile

    def get_profile_by_refid(self, refid: Optional[str]) -> Optional[Node]:
        """
        Given a RefID, return a formatted profile node. Basically every game
        needs a profile lookup, even if it handles where that happens in
        a different request. This is provided for code deduplication.
        """
        if refid is None:
            return None

        # First try to load the actual profile
        userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        profile = self.get_profile(userid)
        if profile is None:
            return None

        # Now try to find out if the profile is new or old
        oldversion = self.previous_version()
        oldprofile = oldversion.get_profile(userid)
        profile['has_old_version'] = oldprofile is not None

        # Now, return it
        return self.format_profile(userid, profile)

    def new_profile_by_refid(self, refid: Optional[str], name: Optional[str]) -> Node:
        """
        Given a RefID and an optional name, create a profile and then return
        a formatted profile node. Similar rationale to get_profile_by_refid.
        """
        if refid is None:
            return None

        if name is None:
            name = 'なし'

        # First, create and save the default profile
        userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        defaultprofile = ValidatedDict({
            'name': name,
        })
        self.put_profile(userid, defaultprofile)

        # Now, reload and format the profile, looking up the has old version flag
        profile = self.get_profile(userid)

        oldversion = self.previous_version()
        oldprofile = oldversion.get_profile(userid)
        profile['has_old_version'] = oldprofile is not None

        return self.format_profile(userid, profile)

    def get_scores_by_extid(self, extid: Optional[int]) -> Optional[Node]:
        """
        Given an ExtID, return a formatted score node. Similar rationale to
        get_profile_by_refid.
        """
        if extid is None:
            return None

        userid = self.data.remote.user.from_extid(self.game, self.version, extid)
        scores = self.data.remote.music.get_scores(self.game, self.version, userid)
        if scores is None:
            return None
        profile = self.get_profile(userid)
        if profile is None:
            return None
        return self.format_scores(userid, profile, scores)

    def update_score(
        self,
        userid: UserID,
        timestamp: int,
        songid: int,
        chart: int,
        points: int,
        medal: int,
        combo: int,
        ghost: Optional[List[int]]=None,
        stats: Optional[Dict[str, int]]=None,
    ) -> None:
        """
        Given various pieces of a score, update the user's high score and score
        history in a controlled manner, so all games in Jubeat series can expect
        the same attributes in a score.
        """
        # Range check medals
        if medal not in [
            self.PLAY_MEDAL_FAILED,
            self.PLAY_MEDAL_CLEARED,
            self.PLAY_MEDAL_NEARLY_FULL_COMBO,
            self.PLAY_MEDAL_FULL_COMBO,
            self.PLAY_MEDAL_NEARLY_EXCELLENT,
            self.PLAY_MEDAL_EXCELLENT,
        ]:
            raise Exception("Invalid medal value {}".format(medal))

        oldscore = self.data.local.music.get_score(
            self.game,
            self.version,
            userid,
            songid,
            chart,
        )

        # Score history is verbatum, instead of highest score
        history = ValidatedDict({})
        oldpoints = points

        if oldscore is None:
            # If it is a new score, create a new dictionary to add to
            scoredata = ValidatedDict({})
            raised = True
            highscore = True
        else:
            # Set the score to any new record achieved
            raised = points > oldscore.points
            highscore = points >= oldscore.points
            points = max(oldscore.points, points)
            scoredata = oldscore.data

        # Replace medal with highest value
        scoredata.replace_int('medal', max(scoredata.get_int('medal'), medal))
        history.replace_int('medal', medal)

        # Increment counters based on medal
        if medal == self.PLAY_MEDAL_CLEARED:
            scoredata.increment_int('clear_count')
        if medal == self.PLAY_MEDAL_FULL_COMBO:
            scoredata.increment_int('full_combo_count')
        if medal == self.PLAY_MEDAL_EXCELLENT:
            scoredata.increment_int('excellent_count')

        # If we have a combo, replace it
        scoredata.replace_int('combo', max(scoredata.get_int('combo'), combo))
        history.replace_int('combo', combo)

        if stats is not None:
            if raised:
                # We have stats, and there's a new high score, update the stats
                scoredata.replace_dict('stats', stats)
            history.replace_dict('stats', stats)

        if ghost is not None:
            # Update the ghost regardless, but don't bother with it in history
            scoredata.replace_int_array('ghost', len(ghost), ghost)

        # Look up where this score was earned
        lid = self.get_machine_id()

        # Write the new score back
        self.data.local.music.put_score(
            self.game,
            self.version,
            userid,
            songid,
            chart,
            lid,
            points,
            scoredata,
            highscore,
            timestamp=timestamp,
        )

        # Save the history of this score too
        self.data.local.music.put_attempt(
            self.game,
            self.version,
            userid,
            songid,
            chart,
            lid,
            oldpoints,
            history,
            raised,
            timestamp=timestamp,
        )
