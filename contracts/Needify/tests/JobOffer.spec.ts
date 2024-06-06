import dotenv from 'dotenv'; 
dotenv.config()
import { Blockchain, SandboxContract, TreasuryContract, printTransactionFees } from '@ton/sandbox';
import { toNano, contractAddress, beginCell, internal, fromNano, SendMode, Address, Contract, OpenedContract, storeAccountState } from '@ton/core';
import { content } from '../scripts/deployMaster';
import { TokenMaster, storeTransfer } from "../build/TokenMaster/tact_TokenMaster"
import { storeDeploy, storeDeployOk, storeMint, storeRevoke, storeWithdraw, storeApprove, storeGetJob, storeCompleteJob, storeConfirmJob, storeAppeal, storeDeposit, storeChooseDoer } from "../build/TokenMaster/tact_JobOffer"
import { JobOffer } from '../wrappers/JobOffer';
import { TokenWallet } from "../build/TokenMaster/tact_TokenWallet"
import { NativeWallet } from '../build/NativeMaster/tact_NativeWallet';
import { NativeMaster } from '../build/NativeMaster/tact_NativeMaster';

// import { NativeMaster } from '../build/TokenMaster/tact_NativeMaster';
// import { NativeWallet } from '../build/TokenMaster/tact_NativeWallet';
import '@ton/test-utils';
import { assert, log } from 'console';
import { deploy, mint } from './test_utils';
import { AppealContract, storeConfirmAppeal, storeRevokeAppeal } from '../build/TokenMaster/tact_AppealContract';
import exp from 'constants';
import { triggerAsyncId } from 'async_hooks';
import { send } from 'process';


const title = "Sell Store 321"
const description = "Selling1 a bike in excellent condition! Trek brand, 2022 model. Lightweight aluminum frame, disc brakes, 21 speeds. Ideal for city trips and long walks. Includes: headlights, bell, running board. Price 25,000 rub. Negotiable. Call: +7-999-123-45-67." 
const price = toNano(100)
const order = "Sell store 2"

const deployAmount = toNano("0.65")
const TransferAmount = toNano("0.65")
const simple_transfer_amount = toNano("0.2")
const fee_offer = 2000n // 2%
const forward_ton_amount = toNano("0.1")
const PublicCost = toNano("200")

function calculate_fee(withdraw_amount: bigint) {
    // calcluate fee
    let fee = withdraw_amount * fee_offer / 100000n
    return fee
}


describe('JobOffer', () => {
    // Users
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let poster: SandboxContract<TreasuryContract>;
    let doer: SandboxContract<TreasuryContract>;
    let third_user: SandboxContract<TreasuryContract>;
    let fourth_user: SandboxContract<TreasuryContract>;
    let platform: SandboxContract<TreasuryContract>;

    // Tokens
    let master: SandboxContract<TokenMaster>;
    let nativeMaster: SandboxContract<NativeMaster>;

    let posterJW: SandboxContract<TokenWallet>;
    let deployerJW: SandboxContract<TokenWallet>;
    let doerJW: SandboxContract<TokenWallet>;
    let JOJW: SandboxContract<TokenWallet>;
    let platformJW: SandboxContract<TokenWallet>;

    let posterNW: SandboxContract<NativeWallet>;
    let deployerNW: SandboxContract<NativeWallet>;
    let doerNW: SandboxContract<NativeWallet>;
    let JONW: SandboxContract<NativeWallet>;
    let platformNW: SandboxContract<NativeWallet>;


    const JettonDecimal = 9
    let jobOffer: SandboxContract<JobOffer>;
    let DeployOffer: any
    let RunPositiveFlow: Function
    
    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury('deployer'); //EQBGhqLAZseEqRXz4ByFPTGV7SVMlI4hrbs-Sps_Xzx01x8G
        poster = await blockchain.treasury('poster'); //EQD-N3h6Wk-IEIVhXtz--H9qc5Nyk5M2VsTTavuytejk8d0X
        const poster_start_balance = await poster.getBalance()
        doer = await blockchain.treasury('doer'); //EQB1cX3AWEUC64v6rhRjwdEk0fRV6Qn-JBFqXSFY30PitP6c
        platform = await blockchain.treasury('platform'); 
        third_user = await blockchain.treasury('third_user'); //EQD6BRvNYA5F5U4g8YJ9utWbtxQQDoVhjemWlUBaK3eAKBDL
        fourth_user = await blockchain.treasury('fourth_user'); // ????

        // Jetton Master
        let master_init = await TokenMaster.init(
            deployer.address, content
        )
        master = blockchain.openContract(await TokenMaster.fromInit(
            deployer.address, content
        ));

        // Native Master
        let nativeMaster_init = await NativeMaster.init(
            deployer.address, content
        )
        nativeMaster = blockchain.openContract(await NativeMaster.fromInit(
            deployer.address, content
        ));



        await deployer.send(
            {
                value: deployAmount,
                to: master.address,
                body: beginCell().store(
                    storeDeploy(
                        {
                            $$type: "Deploy",
                            queryId: 2n
                        }
                    )
                ).endCell(),
                init: {
                    code: master_init.code,
                    data: master_init.data
                }
            }
        )

        deployerJW = blockchain.openContract(await TokenWallet.fromInit(
            deployer.address, master.address
        ))
        deployerNW = blockchain.openContract(await NativeWallet.fromInit(
            deployer.address, nativeMaster.address
        ))

        posterJW = blockchain.openContract(await TokenWallet.fromInit(
            poster.address, master.address
        ))
        posterNW = blockchain.openContract(await NativeWallet.fromInit(
            poster.address, nativeMaster.address
        ))

        doerJW = blockchain.openContract(await TokenWallet.fromInit(
            doer.address, master.address
        )) 
        doerNW = blockchain.openContract(await NativeWallet.fromInit(
            doer.address, nativeMaster.address
        ))

        platformJW = blockchain.openContract(await TokenWallet.fromInit(
            platform.address, master.address
        ))
        platformNW = blockchain.openContract(await NativeWallet.fromInit(
            platform.address, nativeMaster.address
        ))

        // JOB OFFER CREATION
        jobOffer = blockchain.openContract(await JobOffer.fromInit(
            title, description, price, order, master.address, nativeMaster.address
        )) // EQBitOE0LVopau6Z6kkIuEIAwteOfhy6QIb1tw5VBfjembMo
        let JOJW_address = await master.getGetWalletAddress(jobOffer.address) 
        JOJW = blockchain.openContract(
            TokenWallet.fromAddress(
                JOJW_address, 
            )
        )
        
        await deployer.send(
            {
                value: deployAmount,
                to: nativeMaster.address,
                body: beginCell().store(
                    storeDeploy(
                        {
                            $$type: "Deploy",
                            queryId: 2n
                        }
                    )
                ).endCell(),
                init: {
                    code: nativeMaster.init?.code,
                    data: nativeMaster.init?.data
                }
            }
        )
        JONW = blockchain.openContract(
            NativeWallet.fromAddress(
                await nativeMaster.getGetWalletAddress(jobOffer.address)
            )
        )

        // let doeraddress = doer.address
        // log(doeraddress, "doeraddress")
        // let doerNWaddress = doerNW.address
        // log(doerNWaddress, "doerNWaddress")
        // let doerJWaddress = doerJW.address
        // log(doerJWaddress, "doerJWaddress")
        // let posteraddress = poster.address
        // log(posteraddress, "posteraddress")
        // let posterNWaddress = posterNW.address
        // log(posterNWaddress, "posterNWaddress")
        // let posterJWaddress = posterJW.address
        // log(posterJWaddress, "posterJWaddress")
        // let jobOfferaddress = jobOffer.address
        // log(jobOfferaddress, "jobOfferaddress")
        // let jobOfferNWaddress = JONW.address
        // log(jobOfferNWaddress, "jobOfferNWaddress")
        // let jobOfferJWaddress = JOJW.address
        // log(jobOfferJWaddress, "jobOfferJWaddress")
        // let platformaddress = platform.address
        // log(platformaddress, "platformaddress")
        // let platformNWaddress = platformNW.address
        // log(platformNWaddress, "platformNWaddress")
        // let platformJWaddress = platformJW.address
        // log(platformJWaddress, "platformJWaddress")
        // log(nativeMaster.address, "nativeMaster.address")
        // log(master.address, "master.address")
        // let doeraddress = doer.address.toRawString()
        // log(doeraddress, "doeraddress")
        // let doerNWaddress = doerNW.address.toRawString()
        // log(doerNWaddress, "doerNWaddress")
        // let doerJWaddress = doerJW.address.toRawString()
        // log(doerJWaddress, "doerJWaddress")
        // let posteraddress = poster.address.toRawString()
        // log(posteraddress, "posteraddress")
        // let posterNWaddress = posterNW.address.toRawString()
        // log(posterNWaddress, "posterNWaddress")
        // let posterJWaddress = posterJW.address.toRawString()
        // log(posterJWaddress, "posterJWaddress")
        // let jobOfferaddress = jobOffer.address.toRawString()
        // log(jobOfferaddress, "jobOfferaddress")
        // let jobOfferNWaddress = JONW.address.toRawString()
        // log(jobOfferNWaddress, "jobOfferNWaddress")
        // let jobOfferJWaddress = JOJW.address.toRawString()
        // log(jobOfferJWaddress, "jobOfferJWaddress")
        // let platformaddress = platform.address.toRawString()
        // log(platformaddress, "platformaddress")
        // let platformNWaddress = platformNW.address.toRawString()
        // log(platformNWaddress, "platformNWaddress")
        // let platformJWaddress = platformJW.address.toRawString()
        // log(platformJWaddress, "platformJWaddress")
        // log(nativeMaster.address.toRawString(), "nativeMaster.address")
        // log(master.address.toRawString(), "master.address")
        // DEPLOY
        DeployOffer = async () => {
            let deployMsg = beginCell().store(storeDeploy({
                $$type: "Deploy",
                queryId: 1n
            })).endCell()
            let TokenTransferMsg = beginCell().store(storeTransfer({
                $$type: "Transfer",
                query_id: 1n,
                amount: price,
                destination: jobOffer.address,
                response_destination: poster.address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: forward_ton_amount,
                forward_payload: beginCell().endCell()
            })).endCell()

            let NativeTransferMsg = beginCell().store(storeTransfer({
                $$type: "Transfer",
                query_id: 1n,
                amount: PublicCost,
                destination: jobOffer.address,
                response_destination: poster.address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: forward_ton_amount,
                forward_payload: beginCell().endCell()
            })).endCell()

            let res = await poster.sendMessages(
                    [
                        internal({
                        to: jobOffer.address,
                        value: TransferAmount,
                        body: deployMsg,
                        bounce: false,
                        init: {
                            code: jobOffer.init?.code,
                            data: jobOffer.init?.data
                        }
                    }), 
                        internal({
                            to: posterNW.address,
                            value: TransferAmount,
                            body: NativeTransferMsg,
                            bounce: false,
                        }),
                        internal({
                            to: posterJW.address,
                            value: TransferAmount,
                            body: TokenTransferMsg,
                            bounce: false,
                        }),
                    ],
            )
            log(printTransactionFees(res.transactions))
            let jo_state = await jobOffer.getJobData()
            log(jo_state, "jobOffer data")
            log(fromNano(jo_state.jetton_balance), "jobOffer jetton balance")
            log(fromNano(jo_state.wallet_balance), "jobOffer wallet balance")
            // log(fromNano(jo_state.balance), "jobOffer balance")
            // expect(jo_state.state).toBe(7n) // Pre published
            // let jojw_state = await JOJW.getGetWalletData()
            // expect(jojw_state.balance).toBe(price)
            // let jonw_state = await JONW.getGetWalletData()
            // expect(jonw_state.balance).toBe(PublicCost)
        }
        // POSITIVE FLOW until to_state
        RunPositiveFlow = async (to_state: bigint, with_mint: Boolean = true) => {
            if (with_mint) {
                let mint_amount = price
                await mint(deployer, master, poster.address, mint_amount)
                await mint(deployer, nativeMaster, poster.address, PublicCost * 2n)
            }
            await DeployOffer() 
            // let posterNW_data_f = await posterNW.getGetWalletData()
            // log(fromNano(posterNW_data_f.balance), "posterNW_data)f")
            // let posterJW_data_f = await posterJW.getGetWalletData()
            // log(fromNano(posterJW_data_f.balance), "posterJW_data)f")
            // offer deployed and already pre-published state because of deposit was sended
            
            // Offer published
            let JOstateCheck = await jobOffer.getJobData()
            expect(JOstateCheck.state).toEqual(1n) // Offer published
            if (to_state == 1n) {
                return
            }


            // Add doer to put doer to doer map
            let get_job_res = await doer.send(
                {
                    value: TransferAmount,
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeGetJob({
                            $$type: "GetJob",
                            query_id: 1n
                        })
                    ).endCell()
                }
            )
            // log(printTransactionFees(get_job_res.transactions), "ChooseDoer")


            let get_job_res2 = await third_user.send(
                {
                    value: TransferAmount,
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeGetJob({
                            $$type: "GetJob",
                            query_id: 1n
                        })
                    ).endCell()
                }
            )

            // Choose doer
            await poster.send(
                {
                    value: TransferAmount,
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeChooseDoer({
                            $$type: "ChooseDoer",
                            doer: doer.address,
                        })
                    ).endCell()
                }
            )
            let getJobData = await jobOffer.getJobData()
            expect(getJobData.state).toBe(2n) // Accepted by poster
            expect(get_job_res.transactions).toHaveTransaction({
                from: doer.address,
                to: jobOffer.address,
                success: true,
            });
            // OfferAccepted by doer
            if (to_state == 2n) {
                return
            }

            // Complete job by another users
            let complete_msg = {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeCompleteJob({
                        $$type: "CompleteJob",
                        query_id: 1n
                    })
                ).endCell()
            }
            // Complete by Doer
            let completeByDoer = await doer.send(
                complete_msg
            )
            let JOStateData = await jobOffer.getJobData()
            expect(JOStateData.state).toBe(3n) // Completed
            expect(completeByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: true})
            // Completed
            if (to_state == 3n) {
                return
            }
            
            // // Confirming Job 
            let confirmJobMsg = {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeConfirmJob({
                        $$type: "ConfirmJob",
                        query_id: 1n,
                        mark: 5n,
                        review: "Good job!"
                    })
                ).endCell()
            }
            // confirm by owner 
            let confirmByOwner = await poster.send(
                confirmJobMsg
            )
            // Success
            expect(confirmByOwner.transactions).toHaveTransaction({from: poster.address, to: jobOffer.address, success: true})
            let JobOfferFinalState = await jobOffer.getJobData()
            expect(JobOfferFinalState.state).toBe(6n) // Closed
            let jobOfferJWData = await JOJW.getGetWalletData()
            expect(jobOfferJWData.balance).toBe(0n) // all jettons are transfered to doer
            let doerJW_data = await doerJW.getGetWalletData()
            expect(doerJW_data.balance).toBe(price - calculate_fee(price))  // doer has all jettons
            let platformJW_data = await platformJW.getGetWalletData()
            // log(fromNano(platformJW_data.balance), "platformJW_data")
            expect(platformJW_data.balance).toBe(calculate_fee(price))

            // // Now for native tokens operations
            let jobOfferNWData = await JONW.getGetWalletData()
            expect(jobOfferNWData.balance).toBe(0n)
            let doerNW_data = await doerNW.getGetWalletData()
            expect(doerNW_data.balance).toBe(PublicCost - PublicCost * 20000n / 100000n) // 20% of PublicCost was burned
            let posterNW_data = await posterNW.getGetWalletData()
            expect(posterNW_data.balance).toBe(PublicCost * 2n - PublicCost) // 
            const poster_end_balance = await poster.getBalance()
            let result_balacne = poster_start_balance - poster_end_balance
            log(fromNano(result_balacne), "result balance")
            
        }
        
    });

    it("Test: Run positive flow", async () => {
        await RunPositiveFlow()
    });


    it("Test: should revoke", async () => {
        await RunPositiveFlow(1n)
        let s = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )

        expect(s.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: true,
        });
        let res = await JOJW.getGetWalletData()
        expect(res.balance).toEqual(0n)
        let res2 = await posterNW.getGetWalletData()
        expect(res2.balance).toEqual(PublicCost * 2n - PublicCost * 20000n / 100000n)
        let res3 = await posterJW.getGetWalletData()
        expect(res3.balance).toEqual(price)

    });

    it("Test: should not revoke(not poster)", async () => {
        await RunPositiveFlow(1n)
        let s = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        let res = await JOJW.getGetWalletData()
        expect(s.transactions).toHaveTransaction({
            from:doer.address,
            to: jobOffer.address,
            success: false,
            op: 0x011f
        })
        expect(res.balance).toEqual(price)
    });

    it("Test: appelation and revoke by poster", async () => {
        await RunPositiveFlow(3n)
        let result = await jobOffer.getJobData()
        expect(result.state).toBe(3n)
        // Make appeal by poster
        await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeAppeal({
                        $$type: "Appeal",
                        query_id: 0n,
                        description: "Here is a problem with doer JOB",
                    })
                ).endCell()
            }
        )
        let JOData = await jobOffer.getJobData()
        expect(JOData.appeal_address).toBeDefined()
        let Appeal = blockchain.openContract(
            AppealContract.fromAddress(JOData.appeal_address!)
        )
        // Revoke appeal
        let revokeAppealRes = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevokeAppeal({
                        $$type: "RevokeAppeal",
                        query_id: 0n
                    })
                ).endCell()
            }
        )
        let JOData2 = await jobOffer.getJobData()
        expect(JOData2.appeal_address).toBeNull()
        expect(JOData2.state).toBe(3n) // return to OfferCompleted
        expect(revokeAppealRes.transactions).toHaveTransaction({
            from: jobOffer.address,
            to: Appeal.address,
            success: true,
            destroyed: true
        })
        await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeConfirmJob({
                        $$type: "ConfirmJob",
                        query_id: 0n,
                        mark: 5n,
                        review: "Good job!"
                    })
                ).endCell()
            }
        )
        let JOJWData = await JOJW.getGetWalletData()
        expect(JOJWData.balance).toBe(0n)
        let doerJWdata = await doerJW.getGetWalletData()
        expect(doerJWdata.balance).toBe(price - calculate_fee(price))
        let platformJWData = await platformJW.getGetWalletData()
        expect(platformJWData.balance).toBe(calculate_fee(price))

    });

    it("Test: appelation and confirm appeal by platform to poster", async () => {
        await RunPositiveFlow(3n)
        let result = await jobOffer.getJobData()
        expect(result.state).toBe(3n)
        // Make appeal by poster
        await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeAppeal({
                        $$type: "Appeal",
                        query_id: 0n,
                        description: "Here is a problem with doer JOB",
                    })
                ).endCell()
            }
        )
        let JOData = await jobOffer.getJobData()
        expect(JOData.appeal_address).toBeDefined()
        let Appeal = blockchain.openContract(
            AppealContract.fromAddress(JOData.appeal_address!)
        )

        let confirmAppealMessage = {
            value: TransferAmount,
            to: Appeal.address,
            body: beginCell().store(
                storeConfirmAppeal({
                    $$type: "ConfirmAppeal",
                    query_id: 0n,
                    verdict: true
                })
            ).endCell()
        }
        // Try to appeal by another user
        let resD = await doer.send(
            confirmAppealMessage
        )
        expect(resD.transactions).toHaveTransaction({
            from: doer.address,
            to: Appeal.address,
            success: false
        })
        let resP = await poster.send(
            confirmAppealMessage
        )
        expect(resP.transactions).toHaveTransaction({
            from: poster.address,
            to: Appeal.address,
            success: false
        })

        // Confirm appeal by platform
        let res = await platform.send(
            confirmAppealMessage
        )
        expect(res.transactions).toHaveTransaction({
            from: platform.address,
            to: Appeal.address,
            success: true
        })
        let JOJWData = await JOJW.getGetWalletData()
        expect(JOJWData.balance).toBe(0n) // all jettons are transfered to poster 
        let posterJWdata = await posterJW.getGetWalletData()
        expect(posterJWdata.balance).toBe(price) // poster has all jettons 
    });

    it("Test: appelation and confirm appeal by platform to doer", async () => {
        await RunPositiveFlow(3n)
        let result = await jobOffer.getJobData()
        expect(result.state).toBe(3n)
        // Make appeal by poster
        await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeAppeal({
                        $$type: "Appeal",
                        query_id: 0n,
                        description: "Here is a problem with doer JOB",
                    })
                ).endCell()
            }
        )
        let JOData = await jobOffer.getJobData()
        expect(JOData.appeal_address).toBeDefined()
        let Appeal = blockchain.openContract(
            AppealContract.fromAddress(JOData.appeal_address!)
        )

        let confirmAppealMessage = {
            value: TransferAmount,
            to: Appeal.address,
            body: beginCell().store(
                storeConfirmAppeal({
                    $$type: "ConfirmAppeal",
                    query_id: 0n,
                    verdict: false
                })
            ).endCell()
        }
        // Try to appeal by another user
        let resD = await doer.send(
            confirmAppealMessage
        )
        expect(resD.transactions).toHaveTransaction({
            from: doer.address,
            to: Appeal.address,
            success: false
        })
        let resP = await poster.send(
            confirmAppealMessage
        )
        expect(resP.transactions).toHaveTransaction({
            from: poster.address,
            to: Appeal.address,
            success: false
        })

        // Confirm appeal by platform
        let res = await platform.send(
            confirmAppealMessage
        )
        expect(res.transactions).toHaveTransaction({
            from: platform.address,
            to: Appeal.address,
            success: true
        })
        let JOJWData = await JOJW.getGetWalletData()
        expect(JOJWData.balance).toBe(0n) // all jettons are transfered to poster 
        let doerJWData = await doerJW.getGetWalletData()
        expect(doerJWData.balance).toBe(price - calculate_fee(price)) // doer has all jettons without fee
        let platformJWData = await platformJW.getGetWalletData()
        expect(platformJWData.balance).toBe(calculate_fee(price))
    });

    it("Test: appelation from doer", async () => {
        await RunPositiveFlow(3n)
        let result = await jobOffer.getJobData()
        expect(result.state).toBe(3n)
        // Make appeal by poster
        await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeAppeal({
                        $$type: "Appeal",
                        query_id: 0n,
                        description: "Here is a problem with poster approving",
                    })
                ).endCell()
            }
        )
        let JOData = await jobOffer.getJobData()
        expect(JOData.appeal_address).toBeDefined()
        let Appeal = blockchain.openContract(
            AppealContract.fromAddress(JOData.appeal_address!)
        )

        let revokeAppealRes = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevokeAppeal({
                        $$type: "RevokeAppeal",
                        query_id: 0n
                    })
                ).endCell()
            }
        )
        let JOData2 = await jobOffer.getJobData()
        expect(JOData2.appeal_address).toBeNull()
        expect(JOData2.state).toBe(3n) // return to OfferCompleted
        expect(revokeAppealRes.transactions).toHaveTransaction({
            from: jobOffer.address,
            to: Appeal.address,
            success: true,
            destroyed: true
        })
        await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeConfirmJob({
                        $$type: "ConfirmJob",
                        query_id: 0n,
                        mark: 5n,
                        review: "Good job!"
                    })
                ).endCell()
            }
        )
        let JOJWData = await JOJW.getGetWalletData()
        expect(JOJWData.balance).toBe(0n)
        let doerJWdata = await doerJW.getGetWalletData()
        expect(doerJWdata.balance).toBe(price - calculate_fee(price))
        let platformJWData = await platformJW.getGetWalletData()
        expect(platformJWData.balance).toBe(calculate_fee(price))
        log(await jobOffer.getJobData(), "jobOffer data")
    });
});
